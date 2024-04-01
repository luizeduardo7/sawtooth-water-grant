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

from sawtooth_sdk.processor.exceptions import InvalidTransaction

from water_grant_protobuf import payload_pb2


class Payload(object):

    def __init__(self, payload):
        self._transaction = payload_pb2.Payload()
        self._transaction.ParseFromString(payload)

    @property
    def action(self):
        return self._transaction.action

    @property
    def data(self):
        if self._transaction.HasField('create_admin') and \
            self._transaction.action == \
                payload_pb2.Payload.CREATE_ADMIN:
            return self._transaction.create_admin

        if self._transaction.HasField('create_user') and \
            self._transaction.action == \
                payload_pb2.Payload.CREATE_USER:
            return self._transaction.create_user
        
        if self._transaction.HasField('update_user') and \
            self._transaction.action == \
                payload_pb2.Payload.UPDATE_USER:
            return self._transaction.update_user

        if self._transaction.HasField('create_sensor') and \
            self._transaction.action == \
                payload_pb2.Payload.CREATE_SENSOR:
            return self._transaction.create_sensor

        if self._transaction.HasField('update_sensor') and \
            self._transaction.action == \
                payload_pb2.Payload.UPDATE_SENSOR:
            return self._transaction.update_sensor

        raise InvalidTransaction('Action does not match payload data')

    @property
    def timestamp(self):
        return self._transaction.timestamp
