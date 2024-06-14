from flask import Flask, render_template, request, jsonify
import requests
import base64
import payload_pb2  # Importa o módulo gerado pelo Protobuf

app = Flask(__name__)

SAWTOOTH_REST_API_URL = 'http://rest-api:8008'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blocks')
def get_blocks():
    response = requests.get(f'{SAWTOOTH_REST_API_URL}/blocks')
    blocks = response.json()
    return jsonify(blocks)

@app.route('/state')
def get_state():
    response = requests.get(f'{SAWTOOTH_REST_API_URL}/state')
    state = response.json()
    return jsonify(state)

@app.route('/transactions')
def get_transactions():
    response = requests.get(f'{SAWTOOTH_REST_API_URL}/transactions')
    transactions = response.json()
    return jsonify(transactions)

# Função para decodificar o payload
def decode_payload(payload):
    decoded_bytes = base64.b64decode(payload)
    payload_obj = payload_pb2.Payload()
    payload_obj.ParseFromString(decoded_bytes)
    return {
        'action': payload_pb2.Payload.Action.Name(payload_obj.action),
        'timestamp': payload_obj.timestamp,
        'create_admin': {
            'name': payload_obj.create_admin.name
        } if payload_obj.HasField('create_admin') else None,
        'create_user': {
            'name': payload_obj.create_user.name,
            'quota': payload_obj.create_user.quota,
            'created_by_admin_public_key': payload_obj.create_user.created_by_admin_public_key
        } if payload_obj.HasField('create_user') else None,
        'update_user': {
            'user_public_key': payload_obj.update_user.user_public_key,
            'quota': payload_obj.update_user.quota,
            'updated_by_admin_public_key': payload_obj.update_user.updated_by_admin_public_key
        } if payload_obj.HasField('update_user') else None,
        'create_sensor': {
            'sensor_id': payload_obj.create_sensor.sensor_id,
            'latitude': payload_obj.create_sensor.latitude,
            'longitude': payload_obj.create_sensor.longitude,
            'measurement': payload_obj.create_sensor.measurement
        } if payload_obj.HasField('create_sensor') else None,
        'update_sensor': {
            'sensor_id': payload_obj.update_sensor.sensor_id,
            'measurement': payload_obj.update_sensor.measurement
        } if payload_obj.HasField('update_sensor') else None
    }

# Rota para obter uma transação por ID
@app.route('/transactions/<transaction_id>')
def get_transaction_by_id(transaction_id):
    response = requests.get(f'{SAWTOOTH_REST_API_URL}/transactions/{transaction_id}')
    if response.status_code == 200:
        transaction = response.json()
        # Decodifica o payload para torná-lo legível
        decoded_payload = decode_payload(transaction['data']['payload'])
        transaction['data']['payload'] = decoded_payload
        return jsonify(transaction)
    else:
        return jsonify({'error': 'Transaction not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
