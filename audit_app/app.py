from flask import Flask, render_template, jsonify
import requests
from config import Config
from utils import decode_payload

app = Flask(__name__)
app.config.from_object(Config)

def build_url(endpoint):
    base_url = app.config['SAWTOOTH_REST_API_URL']
    return f"{base_url}/{endpoint}"

def handle_error_response(response):
    if response.status_code == 404:
        return jsonify({'error': 'Not found'}), 404
    elif response.status_code >= 400:
        return jsonify({'error': 'Bad request'}), response.status_code
    else:
        return response.json(), response.status_code

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blocks')
def get_blocks():
    response = requests.get(build_url('blocks'))
    if response.status_code == 200:
        blocks = response.json()
        return jsonify(blocks)
    else:
        return handle_error_response(response)

@app.route('/state')
def get_state():
    response = requests.get(build_url('state'))
    if response.status_code == 200:
        state = response.json()
        return jsonify(state)
    else:
        return handle_error_response(response)

@app.route('/transactions')
def get_transactions():
    response = requests.get(build_url('transactions'))
    if response.status_code == 200:
        transactions = response.json()
        for transaction in transactions.get('data', []):
            transaction['payload'] = decode_payload(transaction['payload'])
        return jsonify(transactions)
    else:
        return handle_error_response(response)

@app.route('/transactions/<transaction_id>')
def get_transaction_by_id(transaction_id):
    response = requests.get(build_url(f"transactions/{transaction_id}"))
    if response.status_code == 200:
        transaction = response.json()
        transaction['data']['payload'] = decode_payload(transaction['data']['payload'])
        return jsonify(transaction)
    else:
        return handle_error_response(response)

@app.route('/blocks/<block_id>')
def get_block_by_id(block_id):
    response = requests.get(build_url(f"blocks/{block_id}"))
    if response.status_code == 200:
        block = response.json()
        return jsonify(block)
    else:
        return handle_error_response(response)

@app.route('/state/<address>')
def get_state_by_address(address):
    response = requests.get(build_url(f"state/{address}"))
    if response.status_code == 200:
        state = response.json()
        return jsonify(state)
    else:
        return handle_error_response(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
