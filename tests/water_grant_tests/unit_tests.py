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
import sys
import time
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError

from sawtooth_cli.rest_client import RestClient

from sawtooth_rest_api.protobuf import batch_pb2

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from water_grant_rest_api import transaction_creation


def make_key():
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    signer = CryptoFactory(context).new_signer(private_key)
    return signer


REST_URL = 'rest-api:8008'
BATCH_KEY = make_key()
TEST_ADMIN_KEY = '038713b42df2e514aa654495ecda8a8f9a6cd75760e99df2ff6f02dccb46446c81'
LOGGER = logging.getLogger(__name__)


class WaterGrantTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        wait_for_rest_apis([REST_URL])
        cls.client = WaterGrantClient(REST_URL)
        cls.signer1 = make_key()
        cls.signer2 = make_key()
        cls.bad_signer = make_key()

    def test_00_timestamp(self):
        """ Tests the timestamp validation rules.

        Notes:
            timestamp validation rules:
                - The timestamp must be less than the current time
        """
        self.assertEqual(
            self.client.create_user(
                key=self.signer1,
                name='alice',
                timestamp=sys.maxsize,
                quota=0,
                admin_public_key=TEST_ADMIN_KEY)[0]['status'],
            "INVALID",
            "Invalid timestamp")

    def test_01_create_user(self):
        """ Tests the CreateUserAction validation rules.

        Notes:
            CreateUserAction validation rules:
                - The public_key must be unique for all accounts
        """

        self.assertEqual(
            self.client.create_user(
                key=self.signer1,
                name='alice',
                timestamp=1,
                quota=0,
                admin_public_key=TEST_ADMIN_KEY)[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.create_user(
                key=self.signer1,
                name='alice',
                timestamp=2,
                quota=0,
                admin_public_key=TEST_ADMIN_KEY)[0]['status'],
            "INVALID",
            "User with the public key {} already exists".format(
                self.signer1.get_public_key().as_hex()))

        self.assertEqual(
            self.client.create_user(
                key=self.signer2,
                name='alice',
                timestamp=1,
                quota=0,
                admin_public_key=TEST_ADMIN_KEY)[0]['status'],
            "COMMITTED")

    def test_02_create_sensor(self):
        """ Tests the CreateSensorAction validation rules.

        Notes:
            CreateSensorAction validation rules:
                - Signer is registered as an user
                - sensor_id is not empty
                - sensor_id does not belong to an existing sensor
                - Latitude and longitude are valid
        """

        self.assertEqual(
            self.client.create_sensor(
                key=self.bad_signer,
                user_quota_usage_value=0,
                latitude=0,
                longitude=0,
                measurement=0,
                sensor_id='1',
                timestamp=1)[0]['status'],
            "INVALID",
            "User with the public key {} does not exist".format(
                self.bad_signer.get_public_key().as_hex()))

        self.assertEqual(
            self.client.create_sensor(
                key=self.signer1,
                user_quota_usage_value=0,
                latitude=0,
                longitude=0,
                measurement=0,
                sensor_id='',
                timestamp=2)[0]['status'],
            "INVALID",
            "No sensor ID provided")

        self.assertEqual(
            self.client.create_sensor(
                key=self.signer1,
                user_quota_usage_value=0,
                latitude=0,
                longitude=0,
                measurement=0,
                sensor_id='foo',
                timestamp=3)[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.create_sensor(
                key=self.signer1,
                user_quota_usage_value=0,
                latitude=0,
                longitude=0,
                measurement=0,
                sensor_id='foo',
                timestamp=4)[0]['status'],
            "INVALID",
            "Identifier 'foo' belongs to an existing sensor")

        self.assertEqual(
            self.client.create_sensor(
                key=self.signer1,
                user_quota_usage_value=0,
                latitude=-91000000,
                longitude=0,
                measurement=0,
                sensor_id='badlat1',
                timestamp=5)[0]['status'],
            "INVALID",
            "Latitude must be between -90 and 90. Got -91")

        self.assertEqual(
            self.client.create_sensor(
                key=self.signer1,
                user_quota_usage_value=0,
                latitude=91000000,
                longitude=0,
                measurement=0,
                sensor_id='badlat2',
                timestamp=6)[0]['status'],
            "INVALID",
            "Latitude must be between -90 and 90. Got 91")

        self.assertEqual(
            self.client.create_sensor(
                key=self.signer1,
                user_quota_usage_value=0,
                latitude=0,
                longitude=-181000000,
                measurement=0,
                sensor_id='badlong1',
                timestamp=7)[0]['status'],
            "INVALID",
            "Longitude must be between -180 and 180. Got -181")

        self.assertEqual(
            self.client.create_sensor(
                key=self.signer1,
                user_quota_usage_value=0,
                latitude=0,
                longitude=181000000,
                measurement=0,
                sensor_id='badlong2',
                timestamp=8)[0]['status'],
            "INVALID",
            "Longitude must be between -180 and 180. Got 181")


    def test_03_update_sensor(self):
        self.client.create_sensor(
            key=self.signer1,
            user_quota_usage_value=0,
            latitude=0,
            longitude=0,
            sensor_id='update1',
            timestamp=0)

        self.assertEqual(
            self.client.update_sensor(
                key=self.signer1,
                latitude=90000000,
                longitude=180000000,
                sensor_id='update1',
                timestamp=1)[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.update_sensor(
                key=self.signer1,
                latitude=0,
                longitude=0,
                sensor_id='notasensor',
                timestamp=2)[0]['status'],
            "INVALID",
            "Sensor with the sensor id notasensor does not exist")

        self.assertEqual(
            self.client.update_sensor(
                key=self.signer2,
                latitude=90000000,
                longitude=180000000,
                sensor_id='update1',
                timestamp=3)[0]['status'],
            "INVALID",
            "Transaction signer is not the owner of the sensor")

        self.assertEqual(
            self.client.update_sensor(
                key=self.signer1,
                latitude=90000001,
                longitude=180000000,
                sensor_id='update1',
                timestamp=4)[0]['status'],
            "INVALID",
            "Latitude must be between -90 and 90. Got 91")

        self.assertEqual(
            self.client.create_sensor(
                key=self.signer1,
                latitude=0,
                longitude=-181000000,
                sensor_id='update1',
                timestamp=5)[0]['status'],
            "INVALID",
            "Longitude must be between -180 and 180. Got -181")

        # def test_transfer_sensor(self):
        #     self.client.create_sensor(
        #             key=self.signer1,
        #             user_quota_usage_value=0,
        #             latitude=0,
        #             longitude=0,
        #             measurement=0,
        #             sensor_id='transfer1',
        #             timestamp=1)

        #     self.client.create_sensor(
        #             key=self.signer1,
        #             user_quota_usage_value=0,
        #             latitude=0,
        #             longitude=0,
        #             measurement=0,
        #             sensor_id='transfer2',
        #             timestamp=2)

        #     self.assertEqual(
        #         self.client.transfer_sensor(
        #             key=self.signer1,
        #             receiving_user=self.signer2.get_public_key().as_hex(),
        #             sensor_id='transfer1',
        #             timestamp=3)[0]['status'],
        #             "COMMITTED")

        #     self.assertEqual(
        #         self.client.transfer_sensor(
        #             key=self.signer1,
        #             receiving_user=self.bad_signer.get_public_key().as_hex(),
        #             sensor_id='transfer2',
        #             timestamp=4)[0]['status'],
        #             "INVALID",
        #             "User with the public key {} does not exist".format(
        #             self.bad_signer.get_public_key().as_hex()))

        #     self.assertEqual(
        #         self.client.transfer_sensor(
        #             key=self.signer1,
        #             receiving_user=self.signer2.get_public_key().as_hex(),
        #             sensor_id='doesntexist',
        #             timestamp=5)[0]['status'],
        #             "INVALID",
        #             "Sensor with the sensor id doesntexist does not exist")

        #     self.assertEqual(
        #         self.client.transfer_sensor(
        #             key=self.signer1,
        #             receiving_user=self.signer2.get_public_key().as_hex(),
        #             sensor_id='transfer1',
        #             timestamp=6)[0]['status'],
        #             "INVALID",
        #             "Transaction signer is not the owner of the sensor")
        
class WaterGrantClient(object):

    def __init__(self, url):
        self._client = RestClient(base_url="http://{}".format(url))

    def create_admin(self, key, name, timestamp):
        batch = transaction_creation.make_create_admin_transaction(
            transaction_signer=key,
            batch_signer=BATCH_KEY,
            name=name,
            timestamp=timestamp)
        batch_id = batch.header_signature
        batch_list = batch_pb2.BatchList(batches=[batch])
        self._client.send_batches(batch_list)
        return self._client.get_statuses([batch_id], wait=10)

    def create_user(self, key, name, timestamp,  quota, admin_public_key):
        batch = transaction_creation.make_create_user_transaction(
            transaction_signer=key,
            batch_signer=BATCH_KEY,
            name=name,
            timestamp=timestamp,
            quota=quota,
            admin_public_key=admin_public_key)
        batch_id = batch.header_signature
        batch_list = batch_pb2.BatchList(batches=[batch])
        self._client.send_batches(batch_list)
        return self._client.get_statuses([batch_id], wait=10)
    
    def update_user(self, key, quota, user_public_key, timestamp, admin_public_key):
        batch = transaction_creation.make_update_user_transaction(
            transaction_signer=key,
            batch_signer=BATCH_KEY,
            quota=quota,
            user_public_key=user_public_key,
            timestamp=timestamp,
            admin_public_key=admin_public_key)
        batch_id = batch.header_signature
        batch_list = batch_pb2.BatchList(batches=[batch])
        self._client.send_batches(batch_list)
        return self._client.get_statuses([batch_id], wait=10)

    def create_sensor(self,
                     key,
                     user_quota_usage_value,
                     latitude,
                     longitude,
                     measurement,
                     sensor_id,
                     timestamp):
        batch = transaction_creation.make_sensor_sensor_transaction(
            transaction_signer=key,
            batch_signer=BATCH_KEY,
            user_quota_usage_value=user_quota_usage_value,
            latitude=latitude,
            longitude=longitude,
            measurement=measurement,
            sensor_id=sensor_id,
            timestamp=timestamp)
        batch_id = batch.header_signature
        batch_list = batch_pb2.BatchList(batches=[batch])
        self._client.send_batches(batch_list)
        return self._client.get_statuses([batch_id], wait=10)

    # Transferência de sensores desativada.
    # def transfer_sensor(self, key, receiving_user, sensor_id, timestamp):
    #     batch = transaction_creation.make_transfer_sensor_transaction(
    #         transaction_signer=key,
    #         batch_signer=BATCH_KEY,
    #         receiving_user=receiving_user,
    #         sensor_id=sensor_id,
    #         timestamp=timestamp)
    #     batch_id = batch.header_signature
    #     batch_list = batch_pb2.BatchList(batches=[batch])
    #     self._client.send_batches(batch_list)
    #     return self._client.get_statuses([batch_id], wait=10)

    def update_sensor(self, key, measurement, sensor_id, timestamp):
        batch = transaction_creation.make_update_sensor_transaction(
            transaction_signer=key,
            batch_signer=BATCH_KEY,
            measurement=measurement,
            sensor_id=sensor_id,
            timestamp=timestamp)
        batch_id = batch.header_signature
        batch_list = batch_pb2.BatchList(batches=[batch])
        self._client.send_batches(batch_list)
        return self._client.get_statuses([batch_id], wait=10)

def wait_until_status(url, status_code=200, tries=5):
    """Pause the program until the given url returns the required status.

    Args:
        url (str): The url to query.
        status_code (int, optional): The required status code
        tries (int, optional): The number of attempts to request the url for
            the given status. Defaults to 5.
    Raises:
        AssertionError: If the status is not received in the given number of
            tries.
    """

    attempts = tries
    while attempts > 0:
        try:
            response = urlopen(url)
            if response.getcode() == status_code:
                return

        except HTTPError as err:
            if err.code == status_code:
                return

            LOGGER.debug('failed to read url: %s', str(err))
        except URLError as err:
            LOGGER.debug('failed to read url: %s', str(err))

        sleep_time = (tries - attempts + 1) * 2
        LOGGER.debug('Retrying in %s secs', sleep_time)
        time.sleep(sleep_time)

        attempts -= 1

    raise AssertionError(
        "{} is not available within {} attempts".format(url, tries))


def wait_for_rest_apis(endpoints, tries=5):
    """Pause the program until all the given REST API endpoints are available.

    Args:
        endpoints (list of str): A list of host:port strings.
        tries (int, optional): The number of attempts to request the url for
            availability.
    """

    for endpoint in endpoints:
        http = 'http://'
        url = endpoint if endpoint.startswith(http) else http + endpoint
        wait_until_status(
            '{}/blocks'.format(url),
            status_code=200,
            tries=tries)
