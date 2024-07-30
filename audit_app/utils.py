import base64
import payload_pb2
from datetime import datetime
import pytz

def convert_timestamp(timestamp):
    utc_dt = datetime.fromtimestamp(timestamp)
    local_tz = pytz.timezone('America/Sao_Paulo')
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt.strftime('%d/%m/%Y %H:%M:%S')

def decode_payload(payload):
    decoded_bytes = base64.b64decode(payload)
    payload_obj = payload_pb2.Payload()
    payload_obj.ParseFromString(decoded_bytes)
    
    decoded_payload = {
        'action': payload_pb2.Payload.Action.Name(payload_obj.action),
        'timestamp': convert_timestamp(payload_obj.timestamp)
    }

    if payload_obj.HasField('create_admin'):
        decoded_payload['create_admin'] = {'name': payload_obj.create_admin.name}
    if payload_obj.HasField('create_user'):
        decoded_payload['create_user'] = {
            'name': payload_obj.create_user.name,
            'quota': payload_obj.create_user.quota,
            'created_by_admin_public_key': payload_obj.create_user.created_by_admin_public_key
        }
    if payload_obj.HasField('update_user'):
        decoded_payload['update_user'] = {
            'user_public_key': payload_obj.update_user.user_public_key,
            'quota': payload_obj.update_user.quota,
            'updated_by_admin_public_key': payload_obj.update_user.updated_by_admin_public_key
        }
    if payload_obj.HasField('create_sensor'):
        decoded_payload['create_sensor'] = {
            'sensor_id': payload_obj.create_sensor.sensor_id,
            'latitude': payload_obj.create_sensor.latitude / 1_000_000,
            'longitude': payload_obj.create_sensor.longitude / 1_000_000,
            'measurement': payload_obj.create_sensor.measurement
        }
    if payload_obj.HasField('update_sensor'):
        decoded_payload['update_sensor'] = {
            'sensor_id': payload_obj.update_sensor.sensor_id,
            'measurement': payload_obj.update_sensor.measurement
        }
    
    return decoded_payload
