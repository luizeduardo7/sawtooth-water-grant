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

from water_grant_addressing import addresser

from water_grant_protobuf import admin_pb2
from water_grant_protobuf import user_pb2
from water_grant_protobuf import sensor_pb2


class WaterGrantState(object):
    def __init__(self, context, timeout=2):
        self._context = context
        self._timeout = timeout

    def get_admin(self, public_key):
        """Gets the admin associated with the public_key

        Args:
            public_key (str): The public key of the admin

        Returns:
            admin_pb2.Admin: Admin with the provided public_key
        """
        address = addresser.get_admin_address(public_key)
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container = admin_pb2.AdminContainer()
            container.ParseFromString(state_entries[0].data)
            for admin in container.entries:
                if admin.public_key == public_key:
                    return admin

        return None    
    
    def set_admin(
            self,
            public_key,
            name,
            created_at):
        """Creates a new admin in state

        Args:
            public_key (str): The public key of the admin
            name (str): The human-readable name of the admin
            created_at (int): Unix UTC timestamp of when the admin was created
        """
        address = addresser.get_admin_address(public_key)
        admin = admin_pb2.Admin(
            public_key=public_key,
            name=name,
            created_at=created_at)
        container = admin_pb2.AdminContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([admin])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def get_user(self, public_key):
        """Gets the user associated with the public_key

        Args:
            public_key (str): The public key of the user

        Returns:
            user_pb2.User: User with the provided public_key
        """
        address = addresser.get_user_address(public_key)
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container = user_pb2.UserContainer()
            container.ParseFromString(state_entries[0].data)
            for user in container.entries:
                if user.public_key == public_key:
                    return user

        return None

    def set_user(
            self,
            public_key,
            name,
            created_at,
            quota,
            created_by_admin_public_key):
        """Creates a new user in state

        Args:
            public_key (str): The public key of the user
            name (str): The human-readable name of the user
            timestamp (int): Unix UTC timestamp of when the user was created
            quota (float): Initial quota of the user
            created_by_admin_public_key: The admin's public_key that created the user
        """
        address = addresser.get_user_address(public_key)
        user = user_pb2.User(
            public_key=public_key,
            name=name,
            created_at=created_at,
            quota=quota,
            created_by_admin_public_key=created_by_admin_public_key,
            updated_by_admin_public_key="")
        container = user_pb2.UserContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([user])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def update_user(self,
                    quota,
                    user_public_key,
                    timestamp,
                    updated_by_admin_public_key):
        address = addresser.get_user_address(user_public_key)
        container = user_pb2.UserContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)

        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for user in container.entries:
                print(user)
                if user.public_key == user_public_key:
                    user.quota = quota
                    user.updated_at = timestamp
                    user.updated_by_admin_public_key = updated_by_admin_public_key
        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def get_sensor(self, sensor_id):
        """Gets the sensor associated with the sensor_id

        Args:
            sensor_id (str): The id of the sensor

        Returns:
            sensor_pb2.Sensor: Sensor with the provided sensor_id
        """
        address = addresser.get_sensor_address(sensor_id)
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container = sensor_pb2.SensorContainer()
            container.ParseFromString(state_entries[0].data)
            for sensor in container.entries:
                if sensor.sensor_id == sensor_id:
                    return sensor

        return None

    def set_sensor(self,
                   public_key,
                   latitude,
                   longitude,
                   measurement,
                   sensor_id,
                   timestamp):
        """Creates a new sensor in state

        Args:
            public_key (str): The public key of the user creating the sensor
            latitude (int): Initial latitude of the sensor
            longitude (int): Initial latitude of the sensor
            measurement (double): Measurement value of the sensor
            sensor_id (str): Unique ID of the sensor
            timestamp (int): Unix UTC timestamp of when the sensor was created
        """
        address = addresser.get_sensor_address(sensor_id)
        owner = sensor_pb2.Sensor.Owner(
            user_public_key=public_key,
            timestamp=timestamp)
        location = sensor_pb2.Sensor.Location(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp)
        measurement_value = sensor_pb2.Sensor.Measurement(
            measurement=measurement,
            timestamp=timestamp)
        sensor = sensor_pb2.Sensor(
            sensor_id=sensor_id,
            created_at=timestamp,
            owners=[owner],
            locations=[location],
            measurements=[measurement_value])
        container = sensor_pb2.SensorContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([sensor])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def update_sensor(self, measurement_value, sensor_id, timestamp):
        """Updates a sensor in state

        Args:
            measurement_value (double): New measurement value
            sensor_id (str): Unique ID of the sensor
            timestamp (int): Unix UTC timestamp of when the sensor was updated
        """
        measurement = sensor_pb2.Sensor.Measurement(
            measurement=measurement_value,
            timestamp=timestamp)
        address = addresser.get_sensor_address(sensor_id)
        container = sensor_pb2.SensorContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for sensor in container.entries:
                if sensor.sensor_id == sensor_id:
                    sensor.measurements.extend([measurement])
        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)
