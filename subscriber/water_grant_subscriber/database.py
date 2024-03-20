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
# -----------------------------------------------------------------------------

import logging
import time

import psycopg2
from psycopg2.extras import RealDictCursor


LOGGER = logging.getLogger(__name__)


CREATE_BLOCK_STMTS = """
CREATE TABLE IF NOT EXISTS blocks (
    block_num  bigint PRIMARY KEY,
    block_id   varchar
);
"""

CREATE_AUTH_STMTS = """
CREATE TABLE IF NOT EXISTS auth (
    public_key            varchar PRIMARY KEY,
    username              varchar UNIQUE,
    hashed_password       varchar,
    encrypted_private_key varchar
)
"""

CREATE_SENSOR_STMTS = """
CREATE TABLE IF NOT EXISTS sensors (
    id               bigserial PRIMARY KEY,
    sensor_id        varchar,
    timestamp        bigint,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_MEASUREMENT_STMTS = """
CREATE TABLE IF NOT EXISTS measurements (
    id               bigserial PRIMARY KEY,
    sensor_id        varchar,
    measurement      float,
    timestamp        bigint,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_SENSOR_LOCATION_STMTS = """
CREATE TABLE IF NOT EXISTS sensor_locations (
    id               bigserial PRIMARY KEY,
    sensor_id        varchar,
    latitude         bigint,
    longitude        bigint,
    timestamp        bigint,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_SENSOR_OWNER_STMTS = """
CREATE TABLE IF NOT EXISTS sensor_owners (
    id               bigserial PRIMARY KEY,
    sensor_id        varchar,
    user_id          varchar,
    timestamp        bigint,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_USER_STMTS = """
CREATE TABLE IF NOT EXISTS users (
    id               bigserial PRIMARY KEY,
    public_key       varchar,
    name             varchar,
    timestamp        bigint,
    quota            float,
    start_block_num  bigint,
    end_block_num    bigint
);
"""


class Database(object):
    """Simple object for managing a connection to a postgres database
    """
    def __init__(self, dsn):
        self._dsn = dsn
        self._conn = None

    def connect(self, retries=5, initial_delay=1, backoff=2):
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
                self._conn = psycopg2.connect(self._dsn)
                print('Successfully connected to database')
                return

            except psycopg2.OperationalError:
                print(
                    'Connection failed.'
                    ' Retrying connection (%s retries remaining)',
                    retries - attempt)
                time.sleep(delay)
                delay *= backoff

        self._conn = psycopg2.connect(self._dsn)
        print('Successfully connected to database')

    def create_tables(self):
        """Creates the Water Grant tables
        """
        with self._conn.cursor() as cursor:
            print('Creating table: blocks')
            cursor.execute(CREATE_BLOCK_STMTS)

            print('Creating table: auth')
            cursor.execute(CREATE_AUTH_STMTS)

            print('Creating table: sensors')
            cursor.execute(CREATE_SENSOR_STMTS)

            print('Creating table: measurements')
            cursor.execute(CREATE_MEASUREMENT_STMTS)

            print('Creating table: sensor_locations')
            cursor.execute(CREATE_SENSOR_LOCATION_STMTS)

            print('Creating table: sensor_owners')
            cursor.execute(CREATE_SENSOR_OWNER_STMTS)

            print('Creating table: users')
            cursor.execute(CREATE_USER_STMTS)

        self._conn.commit()

    def disconnect(self):
        """Closes the connection to the database
        """
        print('Disconnecting from database')
        if self._conn is not None:
            self._conn.close()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def drop_fork(self, block_num):
        """Deletes all resources from a particular block_num
        """
        delete_users = """
        DELETE FROM users WHERE start_block_num >= {}
        """.format(block_num)
        
        update_users = """
        UPDATE users SET end_block_num = null
        WHERE end_block_num >= {}
        """.format(block_num)

        delete_measurements = """
        DELETE FROM measurements WHERE sensor_id =
        (SELECT sensor_id FROM sensors WHERE start_block_num >= {})
        """.format(block_num)
   
        delete_sensor_locations = """
        DELETE FROM sensor_locations WHERE sensor_id =
        (SELECT sensor_id FROM sensors WHERE start_block_num >= {})
        """.format(block_num)
        
        delete_sensor_owners = """
        DELETE FROM sensor_owners WHERE sensor_id =
        (SELECT sensor_id FROM sensors WHERE start_block_num >= {})
        """.format(block_num)
   
        delete_sensors = """
        DELETE FROM sensors WHERE start_block_num >= {}
        """.format(block_num)

        update_sensors = """
        UPDATE sensors SET end_block_num = null
        WHERE end_block_num >= {}
        """.format(block_num)

        delete_blocks = """
        DELETE FROM blocks WHERE block_num >= {}
        """.format(block_num)

        with self._conn.cursor() as cursor:
            cursor.execute(delete_users)
            cursor.execute(update_users)
            cursor.execute(delete_measurements)
            cursor.execute(delete_sensor_locations)
            cursor.execute(delete_sensor_owners)
            cursor.execute(delete_sensors)
            cursor.execute(update_sensors)
            cursor.execute(delete_blocks)

    def fetch_last_known_blocks(self, count):
        """Fetches the specified number of most recent blocks
        """
        fetch = """
        SELECT block_num, block_id FROM blocks
        ORDER BY block_num DESC LIMIT {}
        """.format(count)

        with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(fetch)
            blocks = cursor.fetchall()

        return blocks

    def fetch_block(self, block_num):
        fetch = """
        SELECT block_num, block_id FROM blocks WHERE block_num = {}
        """.format(block_num)

        with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(fetch)
            block = cursor.fetchone()

        return block

    def insert_block(self, block_dict):
        insert = """
        INSERT INTO blocks (
        block_num,
        block_id)
        VALUES ('{}', '{}');
        """.format(
            block_dict['block_num'],
            block_dict['block_id'])

        with self._conn.cursor() as cursor:
            cursor.execute(insert)

    def insert_user(self, user_dict):
        print("NOVO USUARIO")
        update_user = """
        UPDATE users SET end_block_num = {}
        WHERE end_block_num = {} AND public_key = '{}'
        """.format(
            user_dict['start_block_num'],
            user_dict['end_block_num'],
            user_dict['public_key'])

        insert_user = """
        INSERT INTO users (
        public_key,
        name,
        timestamp,
        quota,
        start_block_num,
        end_block_num)
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}');
        """.format(
            user_dict['public_key'],
            user_dict['name'],
            user_dict['timestamp'],
            user_dict['quota'],
            user_dict['start_block_num'],
            user_dict['end_block_num'])

        with self._conn.cursor() as cursor:
            cursor.execute(update_user)
            cursor.execute(insert_user)
        print("NOVO USUARIO FINALIZADO")

    def insert_sensor(self, sensor_dict):
        update_sensor = """
        UPDATE sensors SET end_block_num = {}
        WHERE end_block_num = {} AND sensor_id = '{}'
        """.format(
            sensor_dict['start_block_num'],
            sensor_dict['end_block_num'],
            sensor_dict['sensor_id'])
        
        insert_sensor = """
        INSERT INTO sensors (
        sensor_id,
        start_block_num,
        end_block_num)
        VALUES ('{}', '{}', '{}');
        """.format(
            sensor_dict['sensor_id'],
            sensor_dict['start_block_num'],
            sensor_dict['end_block_num'])

        with self._conn.cursor() as cursor:
            cursor.execute(update_sensor)
            cursor.execute(insert_sensor)
            
        self._insert_sensor_locations(sensor_dict)
        self._insert_measurements(sensor_dict)
        self._insert_sensor_owners(sensor_dict)
        

    def _insert_sensor_locations(self, sensor_dict):
        update_sensor_locations = """
        UPDATE sensor_locations SET end_block_num = {}
        WHERE end_block_num = {} AND sensor_id = '{}'
        """.format(
            sensor_dict['start_block_num'],
            sensor_dict['end_block_num'],
            sensor_dict['sensor_id'])

        insert_sensor_locations = [
            """
            INSERT INTO sensor_locations (
            sensor_id,
            latitude,
            longitude,
            timestamp,
            start_block_num,
            end_block_num)
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}');
            """.format(
                sensor_dict['sensor_id'],
                location['latitude'],
                location['longitude'],
                location['timestamp'],
                sensor_dict['start_block_num'],
                sensor_dict['end_block_num'])
            for location in sensor_dict['locations']
        ]
        with self._conn.cursor() as cursor:
            cursor.execute(update_sensor_locations)
            for insert in insert_sensor_locations:
                cursor.execute(insert)

    def _insert_measurements(self, sensor_dict):
        update_measurements = """
        UPDATE measurements SET end_block_num = {}
        WHERE end_block_num = {} AND sensor_id = '{}'
        """.format(
            sensor_dict['start_block_num'],
            sensor_dict['end_block_num'],
            sensor_dict['sensor_id'])

        insert_measurements = [
            """
            INSERT INTO measurements (
            sensor_id,
            measurement,
            timestamp,
            start_block_num,
            end_block_num)
            VALUES ('{}', '{}', '{}', '{}', '{}');
            """.format(
                sensor_dict['sensor_id'],
                measurement['measurement'],
                measurement['timestamp'],
                sensor_dict['start_block_num'],
                sensor_dict['end_block_num'])
            for measurement in sensor_dict['measurements']
        ]
        with self._conn.cursor() as cursor:
            cursor.execute(update_measurements)
            for insert in insert_measurements:
                cursor.execute(insert)
                
    def _insert_sensor_owners(self, sensor_dict):
            update_sensor_owners = """
            UPDATE sensor_owners SET end_block_num = {}
            WHERE end_block_num = {} AND sensor_id = '{}'
            """.format(
                sensor_dict['start_block_num'],
                sensor_dict['end_block_num'],
                sensor_dict['sensor_id'])

            insert_sensor_owners = [
                """
                INSERT INTO sensor_owners (
                sensor_id,
                user_id,
                timestamp,
                start_block_num,
                end_block_num)
                VALUES ('{}', '{}', '{}', '{}', '{}');
                """.format(
                    sensor_dict['sensor_id'],
                    owner['user_id'],
                    owner['timestamp'],
                    sensor_dict['start_block_num'],
                    sensor_dict['end_block_num'])
                for owner in sensor_dict['owners']
            ]
            with self._conn.cursor() as cursor:
                cursor.execute(update_sensor_owners)
                for insert in insert_sensor_owners:
                    cursor.execute(insert)