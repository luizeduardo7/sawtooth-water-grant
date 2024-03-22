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

import datetime
import time

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from water_grant_addressing import addresser

from water_grant_protobuf import payload_pb2

from water_grant_tp.payload import Payload
from water_grant_tp.state import WaterGrantState


SYNC_TOLERANCE = 60 * 5
MAX_LAT = 90 * 1e6
MIN_LAT = -90 * 1e6
MAX_LNG = 180 * 1e6
MIN_LNG = -180 * 1e6


class WaterGrantHandler(TransactionHandler):

    @property
    def family_name(self):
        return addresser.FAMILY_NAME

    @property
    def family_versions(self):
        return [addresser.FAMILY_VERSION]

    @property
    def namespaces(self):
        return [addresser.NAMESPACE]

    def apply(self, transaction, context):
        header = transaction.header
        payload = Payload(transaction.payload)
        state = WaterGrantState(context)

        _validate_timestamp(payload.timestamp)

        if payload.action == payload_pb2.Payload.CREATE_USER:
            _create_user(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.Payload.UPDATE_USER:
            _update_user(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.Payload.CREATE_SENSOR:
            _create_sensor(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.Payload.UPDATE_SENSOR:
            _update_sensor(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        else:
            raise InvalidTransaction('Unhandled action')


def _create_user(state, public_key, payload):
    if state.get_user(public_key):
        raise InvalidTransaction('User with the public key {} already '
                                 'exists'.format(public_key))
    state.set_user(
        public_key=public_key,
        name=payload.data.name,
        timestamp=payload.timestamp,
        quota=payload.data.quota)


def _update_user(state, public_key, payload):
    user = state.get_user(payload.data.user_id)
    if user is None:
        raise InvalidTransaction('User with the public key {} does not '
                                 'exist'.format(payload.data.user_id))

    # Talvez validar função de admin
    # if not _validate_admin(signer_public_key=public_key):
    #     raise InvalidTransaction(
    #         'Transaction signer is not an admin')

    _validate_quota(payload.data.quota)

    state.update_user(
        quota=payload.data.quota,
        user_id=payload.data.user_id,
        timestamp=payload.timestamp)


def _create_sensor(state, public_key, payload):
    if state.get_user(public_key) is None:
        raise InvalidTransaction('User with the public key {} does '
                                 'not exist'.format(public_key))

    if payload.data.sensor_id == '':
        raise InvalidTransaction('No sensor ID provided')

    if state.get_sensor(payload.data.sensor_id):
        raise InvalidTransaction('Identifier {} belongs to an existing '
                                 'sensor'.format(payload.data.sensor_id))

    _validate_latlng(payload.data.latitude, payload.data.longitude)

    state.set_sensor(
        public_key=public_key,
        latitude=payload.data.latitude,
        longitude=payload.data.longitude,
        measurement=payload.data.measurement,
        sensor_id=payload.data.sensor_id,
        timestamp=payload.timestamp)


def _update_sensor(state, public_key, payload):
    sensor = state.get_sensor(payload.data.sensor_id)
    if sensor is None:
        raise InvalidTransaction('Sensor with the sensor id {} does not '
                                 'exist'.format(payload.data.sensor_id))

    if not _validate_sensor_owner(signer_public_key=public_key,
                                  sensor=sensor):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the sensor')

    _validate_measurement(payload.data.measurement)

    state.update_sensor(
        measurement_value=payload.data.measurement,
        sensor_id=payload.data.sensor_id,
        timestamp=payload.timestamp)


def _validate_sensor_owner(signer_public_key, sensor):
    """Validates that the public key of the signer is the latest (i.e.
    current) owner of the sensor
    """
    latest_owner = max(sensor.owners, key=lambda obj: obj.timestamp).user_id
    return latest_owner == signer_public_key


def _validate_quota(quota):
    if quota < 0:
        raise InvalidTransaction('Cota deve ser maior ou igual a 0.')


def _validate_measurement(measurement):
    if measurement < 0:
        raise InvalidTransaction('Medida deve ser maior ou igual a 0.')


def _validate_latlng(latitude, longitude):
    if not MIN_LAT <= latitude <= MAX_LAT:
        raise InvalidTransaction('Latitude must be between -90 and 90. '
                                 'Got {}'.format(latitude/1e6))
    if not MIN_LNG <= longitude <= MAX_LNG:
        raise InvalidTransaction('Longitude must be between -180 and 180. '
                                 'Got {}'.format(longitude/1e6))


def _validate_timestamp(timestamp):
    """Validates that the client submitted timestamp for a transaction is not
    greater than current time, within a tolerance defined by SYNC_TOLERANCE

    NOTE: Timestamp validation can be challenging since the machines that are
    submitting and validating transactions may have different system times
    """
    dts = datetime.datetime.utcnow()
    current_time = round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)
    if (timestamp - current_time) > SYNC_TOLERANCE:
        raise InvalidTransaction(
            'Timestamp must be less than local time.'
            ' Expected {0} in ({1}-{2}, {1}+{2})'.format(
                timestamp, current_time, SYNC_TOLERANCE))
