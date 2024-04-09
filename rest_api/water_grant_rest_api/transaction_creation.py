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

import hashlib

from sawtooth_rest_api.protobuf import batch_pb2
from sawtooth_rest_api.protobuf import transaction_pb2

from water_grant_addressing import addresser

from water_grant_protobuf import payload_pb2

def make_create_admin_transaction(transaction_signer,
                                  batch_signer,
                                  name,
                                  timestamp):
    """Make a CreateAdminAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        name (str): The admin's name
        timestamp (int): Unix UTC timestamp of when the admin is created

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch

    """

    admin_address = addresser.get_admin_address(
        transaction_signer.get_public_key().as_hex())

    inputs = [admin_address]

    outputs = [admin_address]

    action = payload_pb2.CreateAdminAction(name=name)

    payload = payload_pb2.Payload(
        action=payload_pb2.Payload.CREATE_ADMIN,
        create_admin=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)

def make_create_user_transaction(transaction_signer,
                                  batch_signer,
                                  name,
                                  timestamp,
                                  quota,
                                  admin_public_key):
    """Make a CreateUserAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        name (str): The user's name
        timestamp (int): Unix UTC timestamp of when the user is created
        quota (float): Initial quota of the user
        admin_public_key (str): Admin Public key that created user

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch

    """

    user_address = addresser.get_user_address(
        transaction_signer.get_public_key().as_hex())
    
    admin_address = addresser.get_admin_address(admin_public_key)

    inputs = [user_address, admin_address]

    outputs = [user_address]

    action = payload_pb2.CreateUserAction(
        name=name,
        quota=quota, 
        created_by_admin_public_key=admin_public_key)

    payload = payload_pb2.Payload(
        action=payload_pb2.Payload.CREATE_USER,
        create_user=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)

def make_update_user_transaction(transaction_signer,
                                   batch_signer,
                                   quota,
                                   user_public_key,
                                   timestamp,
                                   admin_public_key):
    """Make a CreateSensorAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        quota: New quota of the user
        user_public_key (str): User public key
        timestamp (int): Unix UTC timestamp of when the user is updated
        admin_public_key (str): Admin Public key that updated user

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """
    user_address = addresser.get_user_address(
        transaction_signer.get_public_key().as_hex())

    admin_address = addresser.get_admin_address(admin_public_key)

    inputs = [user_address, admin_address]

    outputs = [user_address]

    action = payload_pb2.UpdateUserAction(
        user_public_key=user_public_key,
        quota=quota,
        updated_by_admin_public_key=admin_public_key)

    payload = payload_pb2.Payload(
        action=payload_pb2.Payload.UPDATE_USER,
        update_user=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_sensor_transaction(transaction_signer,
                                   batch_signer,
                                   latitude,
                                   longitude,
                                   measurement,
                                   sensor_id,
                                   timestamp):
    """Make a CreateSensorAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        latitude (int): Initial latitude of the sensor
        longitude (int): Initial latitude of the sensor
        measurement: Initial measurement of the sensor
        sensor_id (str): Unique ID of the sensor
        timestamp (int): Unix UTC timestamp of when the user is created

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """

    inputs = [
        addresser.get_user_address(
            transaction_signer.get_public_key().as_hex()),
        addresser.get_sensor_address(sensor_id)
    ]

    outputs = [addresser.get_sensor_address(sensor_id)]

    action = payload_pb2.CreateSensorAction(
        sensor_id=sensor_id,
        latitude=latitude,
        longitude=longitude,
        measurement=measurement)

    payload = payload_pb2.Payload(
        action=payload_pb2.Payload.CREATE_SENSOR,
        create_sensor=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_update_sensor_transaction(transaction_signer,
                                   batch_signer,
                                   measurement,
                                   sensor_id,
                                   timestamp):
    """Make a CreateSensorAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        measurement: New measurement of the sensor
        sensor_id (str): Unique ID of the sensor
        timestamp (int): Unix UTC timestamp of when the sensor is updated

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """
    user_address = addresser.get_user_address(
        transaction_signer.get_public_key().as_hex())
    sensor_address = addresser.get_sensor_address(sensor_id)

    inputs = [user_address, sensor_address]

    outputs = [sensor_address]

    action = payload_pb2.UpdateSensorAction(
        sensor_id=sensor_id,
        measurement=measurement)

    payload = payload_pb2.Payload(
        action=payload_pb2.Payload.UPDATE_SENSOR,
        update_sensor=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def _make_batch(payload_bytes,
                inputs,
                outputs,
                transaction_signer,
                batch_signer):

    transaction_header = transaction_pb2.TransactionHeader(
        family_name=addresser.FAMILY_NAME,
        family_version=addresser.FAMILY_VERSION,
        inputs=inputs,
        outputs=outputs,
        signer_public_key=transaction_signer.get_public_key().as_hex(),
        batcher_public_key=batch_signer.get_public_key().as_hex(),
        dependencies=[],
        payload_sha512=hashlib.sha512(payload_bytes).hexdigest())
    transaction_header_bytes = transaction_header.SerializeToString()

    transaction = transaction_pb2.Transaction(
        header=transaction_header_bytes,
        header_signature=transaction_signer.sign(transaction_header_bytes),
        payload=payload_bytes)

    batch_header = batch_pb2.BatchHeader(
        signer_public_key=batch_signer.get_public_key().as_hex(),
        transaction_ids=[transaction.header_signature])
    batch_header_bytes = batch_header.SerializeToString()

    batch = batch_pb2.Batch(
        header=batch_header_bytes,
        header_signature=batch_signer.sign(batch_header_bytes),
        transactions=[transaction])

    return batch


# Transferência de sensores desativada.
# def make_transfer_sensor_transaction(transaction_signer,
#                                      batch_signer,
#                                      receiving_user,
#                                      sensor_id,
#                                      timestamp):
#     """Make a CreateSensorAction transaction and wrap it in a batch

#     Args:
#         transaction_signer (sawtooth_signing.Signer): The transaction key pair
#         batch_signer (sawtooth_signing.Signer): The batch key pair
#         receiving_user (str): Public key of the user receiving the sensor
#         sensor_id (str): Unique ID of the sensor
#         timestamp (int): Unix UTC timestamp of when the sensor is transferred

#     Returns:
#         batch_pb2.Batch: The transaction wrapped in a batch
#     """
#     sending_user_address = addresser.get_user_address(
#         transaction_signer.get_public_key().as_hex())
#     receiving_user_address = addresser.get_user_address(receiving_user)
#     sensor_address = addresser.get_sensor_address(sensor_id)

#     inputs = [sending_user_address, receiving_user_address, sensor_address]

#     outputs = [sensor_address]

#     action = payload_pb2.TransferSensorAction(
#         sensor_id=sensor_id,
#         receiving_user=receiving_user)

#     payload = payload_pb2.Payload(
#         action=payload_pb2.Payload.TRANSFER_SENSOR,
#         transfer_sensor=action,
#         timestamp=timestamp)
#     payload_bytes = payload.SerializeToString()

#     return _make_batch(
#         payload_bytes=payload_bytes,
#         inputs=inputs,
#         outputs=outputs,
#         transaction_signer=transaction_signer,
#         batch_signer=batch_signer)
