# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import asyncio
import logging

import aiopg
import psycopg2
from psycopg2.extras import RealDictCursor


LATEST_BLOCK_NUM = """
SELECT max(block_num) FROM blocks
"""
LOGGER = logging.getLogger(__name__)


class Database(object):
    """Manages connection to the postgres database and makes async queries
    """
    def __init__(self, host, port, name, user, password, loop):
        self._dsn = 'dbname={} user={} password={} host={} port={}'.format(
            name, user, password, host, port)
        self._loop = loop
        self._conn = None

    async def connect(self, retries=5, initial_delay=1, backoff=2):
        """Initializes a connection to the database

        Args:
            retries (int): Number of times to retry the connection
            initial_delay (int): Number of seconds wait between reconnects
            backoff (int): Multiplies the delay after each retry
        """
        print('Connecting to database')

        delay = initial_delay
        for attempt in range(retries):
            try:
                self._conn = await aiopg.connect(
                    dsn=self._dsn, loop=self._loop, echo=True)
                print('Successfully connected to database')
                return

            except psycopg2.OperationalError:
                print(
                    'Connection failed.'
                    ' Retrying connection (%s retries remaining)',
                    retries - attempt)
                await asyncio.sleep(delay)
                delay *= backoff

        self._conn = await aiopg.connect(
            dsn=self._dsn, loop=self._loop, echo=True)
        print('Successfully connected to database')

    def disconnect(self):
        """Closes connection to the database
        """
        self._conn.close()


    async def create_auth_entry(self,
                                public_key,
                                username,
                                encrypted_private_key,
                                hashed_password,
                                is_admin):
        insert = """
        INSERT INTO auth (
            public_key,
            username,
            encrypted_private_key,
            hashed_password,
            is_admin
        )
        VALUES ('{}', '{}', '{}', '{}', '{}');
        """.format(
            public_key,
            username,
            encrypted_private_key.hex(),
            hashed_password.hex(),
            is_admin)

        async with self._conn.cursor() as cursor:
            await cursor.execute(insert)

        self._conn.commit()
        
    async def fetch_admin_resource(self, public_key):
        fetch = """
        SELECT public_key, name, created_at
        FROM admins
        WHERE public_key='{0}'
        AND ({1}) >= start_block_num
        AND ({1}) < end_block_num;
        """.format(public_key, LATEST_BLOCK_NUM)

        async with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(fetch)
            return await cursor.fetchone()
        
    async def fetch_all_admin_resources(self):
        fetch = """
        SELECT public_key, name, created_at FROM admins
        WHERE ({0}) >= start_block_num
        AND ({0}) < end_block_num;
        """.format(LATEST_BLOCK_NUM)

        async with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(fetch)
            return await cursor.fetchall()


    async def fetch_user_resource(self, public_key):
        fetch = """
        SELECT public_key, name, created_at, quota, created_by_admin_public_key,
        updated_by_admin_public_key, updated_at
        FROM users
        WHERE public_key='{0}'
        AND ({1}) >= start_block_num
        AND ({1}) < end_block_num;
        """.format(public_key, LATEST_BLOCK_NUM)

        async with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(fetch)
            return await cursor.fetchone()

    async def fetch_all_user_resources(self):
        fetch = """
        SELECT public_key, name, created_at FROM users
        WHERE ({0}) >= start_block_num
        AND ({0}) < end_block_num;
        """.format(LATEST_BLOCK_NUM)

        async with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(fetch)
            return await cursor.fetchall()

    # É usado username_or_public_key, porque algumas funções chamam
    # fetch_auth_resource usando um dos dois, pode ser corrigido 
    # criando outro fetch_auth
    async def fetch_auth_resource(self, username_or_public_key):
        fetch = """
        SELECT * FROM auth WHERE username='{}' OR public_key='{}'
        """.format(username_or_public_key, username_or_public_key)

        async with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(fetch)
            return await cursor.fetchone()

    async def fetch_sensor_resource(self, sensor_id):
        fetch_sensor = """
        SELECT sensor_id FROM sensors
        WHERE sensor_id='{0}'
        AND ({1}) >= start_block_num
        AND ({1}) < end_block_num;
        """.format(sensor_id, LATEST_BLOCK_NUM)

        fetch_sensor_locations = """
        SELECT latitude, longitude, timestamp FROM sensor_locations
        WHERE sensor_id='{0}'
        AND ({1}) >= start_block_num
        AND ({1}) < end_block_num;
        """.format(sensor_id, LATEST_BLOCK_NUM)

        fetch_sensor_owners = """
        SELECT user_id, timestamp FROM sensor_owners
        WHERE sensor_id='{0}'
        AND ({1}) >= start_block_num
        AND ({1}) < end_block_num;
        """.format(sensor_id, LATEST_BLOCK_NUM)
        
        fetch_sensor_measurement = """
        SELECT measurement, timestamp FROM measurements
        WHERE sensor_id='{0}'
        AND ({1}) >= start_block_num
        AND ({1}) < end_block_num;
        """.format(sensor_id, LATEST_BLOCK_NUM)

        async with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                await cursor.execute(fetch_sensor)
                sensor = await cursor.fetchone()

                await cursor.execute(fetch_sensor_locations)
                sensor['locations'] = await cursor.fetchall()

                await cursor.execute(fetch_sensor_owners)
                sensor['owners'] = await cursor.fetchall()
                
                await cursor.execute(fetch_sensor_measurement)
                sensor['measurements'] = await cursor.fetchall()

                return sensor
            except TypeError:
                return None

    async def fetch_all_sensor_resources(self):
        fetch_sensors = """
        SELECT sensor_id FROM sensors
        WHERE ({0}) >= start_block_num
        AND ({0}) < end_block_num;
        """.format(LATEST_BLOCK_NUM)

        async with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                await cursor.execute(fetch_sensors)
                sensors = await cursor.fetchall()

                for sensor in sensors:
                    fetch_sensor_locations = """
                    SELECT latitude, longitude, timestamp
                    FROM sensor_locations
                    WHERE sensor_id='{0}'
                    AND ({1}) >= start_block_num
                    AND ({1}) < end_block_num;
                    """.format(sensor['sensor_id'], LATEST_BLOCK_NUM)

                    fetch_sensor_owners = """
                    SELECT user_id, timestamp
                    FROM sensor_owners
                    WHERE sensor_id='{0}'
                    AND ({1}) >= start_block_num
                    AND ({1}) < end_block_num;
                    """.format(sensor['sensor_id'], LATEST_BLOCK_NUM)
                    
                    fetch_sensor_measurement = """
                    SELECT measurement, timestamp
                    FROM measurements
                    WHERE sensor_id='{0}'
                    AND ({1}) >= start_block_num
                    AND ({1}) < end_block_num;
                    """.format(sensor['sensor_id'], LATEST_BLOCK_NUM)

                    await cursor.execute(fetch_sensor_locations)
                    sensor['locations'] = await cursor.fetchall()

                    await cursor.execute(fetch_sensor_owners)
                    sensor['owners'] = await cursor.fetchall()
                    
                    await cursor.execute(fetch_sensor_measurement)
                    sensor['measurements'] = await cursor.fetchall()

                return sensors
            except TypeError:
                return []
