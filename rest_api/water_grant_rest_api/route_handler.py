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
import datetime
from json.decoder import JSONDecodeError
import logging
import time

from aiohttp.web import json_response
import bcrypt
from Crypto.Cipher import AES
from itsdangerous import BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from water_grant_rest_api.errors import ApiBadRequest
from water_grant_rest_api.errors import ApiNotFound
from water_grant_rest_api.errors import ApiUnauthorized


LOGGER = logging.getLogger(__name__)


class RouteHandler(object):
    def __init__(self, loop, messenger, database):
        self._loop = loop
        self._messenger = messenger
        self._database = database

    async def authenticate(self, request):
        body = await decode_request(request)
        required_fields = ['username', 'password']
        validate_fields(required_fields, body)

        username = body.get('username')
        password = bytes(body.get('password'), 'utf-8')

        auth_info = await self._database.fetch_auth_resource(username)
        if auth_info is None:
            raise ApiUnauthorized("Username não encontrado.")

        hashed_password = auth_info.get('hashed_password')
        if not bcrypt.checkpw(password, bytes.fromhex(hashed_password)):
            raise ApiUnauthorized('Senha ou username incorreto.')

        token = generate_auth_token(
            request.app['secret_key'], auth_info.get('public_key'))
        
        is_admin = auth_info.get('is_admin')

        return json_response({
            'authorization': token,
            'adminflag': is_admin,
            'username': username})
    
    async def create_admin(self, request):
        await self._authorize(request)
        
        body = await decode_request(request)
        required_fields = ['username', 'name', 'password']
        validate_fields(required_fields, body)

        public_key, private_key = self._messenger.get_new_key_pair()

        username = body.get('username')
        auth_info = await self._database.fetch_auth_resource(username)
        if auth_info is not None:
            raise ApiUnauthorized(
                'Já existe um admin com esse username.'
                'Por favor, insira outro.')
        
        encrypted_private_key = encrypt_private_key(
            request.app['aes_key'], public_key, private_key)
        hashed_password = hash_password(body.get('password'))

        await self._database.create_auth_entry(
            public_key,
            username, 
            encrypted_private_key, 
            hashed_password,
            is_admin=True)
        
        try:
            await self._messenger.send_create_admin_transaction(
                private_key=private_key,
                name=body.get('name'),
                timestamp=get_time())
        except:
            # Caso a transação não seja valida, a conta é removida da
            # tabela auth
            await self._database.delete_auth_entry(public_key)
            raise ApiUnauthorized(
                'Transação invalida')

        token = generate_auth_token(
            request.app['secret_key'], public_key)

        return json_response({'authorization': token})

    async def create_user(self, request):
        await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['username', 'name', 'password', 'created_by_admin_public_key']
        validate_fields(required_fields, body)

        # Valida se há permissão de admin
        admin_public_key = body.get('created_by_admin_public_key')
        admin_auth_info = await self._database.fetch_auth_resource(admin_public_key)
        if admin_auth_info['is_admin'] is False:
            raise ApiBadRequest("Você não tem permissão para realizar esta ação!")
        
        public_key, private_key = self._messenger.get_new_key_pair()

        username = body.get('username')
        user_auth_info = await self._database.fetch_auth_resource(username)
        if user_auth_info is not None:
            raise ApiUnauthorized(
                'Já existe um usuário com esse username.'
                'Por favor, insira outro.')
        
        encrypted_private_key = encrypt_private_key(
            request.app['aes_key'], public_key, private_key)
        hashed_password = hash_password(body.get('password'))
    
        await self._database.create_auth_entry(
            public_key,
            username, 
            encrypted_private_key, 
            hashed_password,
            is_admin=False)
        
        try:
            await self._messenger.send_create_user_transaction(
                private_key=private_key,
                name=body.get('name'),
                timestamp=get_time(),
                admin_public_key=admin_public_key)
        except:
            # Caso a transação não seja valida, a conta é removida da
            # tabela auth
            await self._database.delete_auth_entry(public_key)
            raise ApiUnauthorized(
                'Transação invalida')

        token = generate_auth_token(
            request.app['secret_key'], public_key)

        return json_response({'authorization': token})

    async def list_users(self, _request):
        user_list = await self._database.fetch_all_user_resources()
        return json_response(user_list)

    async def fetch_user(self, request):
        public_key = request.match_info.get('user_public_key', '')
        user = await self._database.fetch_user_resource(public_key)
        if user is None:
            raise ApiNotFound(
                'usuário com a chave pública {} não foi encontrado.'
                .format(public_key))
        return json_response(user)
    
    async def update_user(self, request):
        body = await decode_request(request)
        # Primeira validação, verifica se há a nova cota e
        # a chave pública do admin na requisição
        required_fields = ['quota', 'updated_by_admin_public_key']
        validate_fields(required_fields, body)

         # Valida se há permissão de admin
        admin_public_key = body.get('updated_by_admin_public_key')
        admin_auth_info = await self._database.fetch_auth_resource(admin_public_key)
        if admin_auth_info['is_admin'] is False:
            raise ApiBadRequest("Você não tem permissão para realizar esta ação!")

        private_key = await self._authorize(request)

        user_public_key = request.match_info.get('user_public_key', '')

        await self._messenger.send_update_user_transaction(
            private_key=private_key,
            quota=body['quota'],
            user_public_key=user_public_key,
            timestamp=get_time(),
            admin_public_key=body['updated_by_admin_public_key'])

        return json_response(
            {'data': 'Update user transaction submitted'})

    async def create_sensor(self, request):
        private_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['latitude', 'longitude', 'sensor_id']
        validate_fields(required_fields, body)

        await self._messenger.send_create_sensor_transaction(
            private_key=private_key,
            latitude=body.get('latitude'),
            longitude=body.get('longitude'),
            sensor_id=body.get('sensor_id'),
            timestamp=get_time())

        return json_response(
            {'data': 'Create sensor transaction submitted'})

    async def list_sensors(self, _request):
        sensor_list = await self._database.fetch_all_sensor_resources()
        return json_response(sensor_list)

    async def fetch_sensor(self, request):
        sensor_id = request.match_info.get('sensor_id', '')
        sensor = await self._database.fetch_sensor_resource(sensor_id)
        if sensor is None:
            raise ApiNotFound(
                'sensor com o ID '
                '{} não foi encontrado.'.format(sensor_id))
        return json_response(sensor)
    
    async def update_sensor(self, request):
        private_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['measurement']
        validate_fields(required_fields, body)

        sensor_id = request.match_info.get('sensor_id', '')

        await self._messenger.send_update_sensor_transaction(
            private_key=private_key,
            measurement=body['measurement'],
            sensor_id=sensor_id,
            timestamp=get_time())

        return json_response(
            {'data': 'Update sensor transaction submitted'})

    async def _authorize(self, request):
        token = request.headers.get('AUTHORIZATION')
        if token is None:
            raise ApiUnauthorized('Não foi provido token de autenticação.')
        token_prefixes = ('Bearer', 'Token')
        for prefix in token_prefixes:
            if prefix in token:
                token = token.partition(prefix)[2].strip()
        try:
            token_dict = deserialize_auth_token(request.app['secret_key'],
                                                token)
        except BadSignature:
            raise ApiUnauthorized('Token de autenticação invalido.')
        
        public_key = token_dict.get('public_key')
        body = await decode_request(request)

        # Verifica se é há um chave de admin válida
        admin_auth = await self._database.fetch_auth_resource(public_key)
        if admin_auth is None:
            raise ApiUnauthorized('Token não está associado com um usuário.')

        # Verifica se trata da operação de atualização de usuário
        if body.get('user_public_key'):
            public_key = body.get('user_public_key')  

        auth_resource = await self._database.fetch_auth_resource(public_key)
        if auth_resource is None:
            raise ApiUnauthorized('Token não está associado com um usuário.')
        return decrypt_private_key(request.app['aes_key'],
                                   public_key,
                                   auth_resource['encrypted_private_key'])


async def validate_admin(admin_public_key, database):
        auth_resource = await database.fetch_auth_resource(admin_public_key)
        print(auth_resource['is_admin'])
        print(type(auth_resource['is_admin']))
        if auth_resource['is_admin'] is False:
            raise ApiBadRequest("Você não tem permissão para realizar esta ação!")

async def decode_request(request):
    try:
        return await request.json()
    except JSONDecodeError:
        raise ApiBadRequest('Formato JSON imprópio.')


def validate_fields(required_fields, body):
    for field in required_fields:
        if body.get(field) is None:
            raise ApiBadRequest(
                "O parâmetro '{}' é requerido.".format(field))

def encrypt_private_key(aes_key, public_key, private_key):
    init_vector = bytes.fromhex(public_key[:32])
    cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC, init_vector)
    return cipher.encrypt(private_key)


def decrypt_private_key(aes_key, public_key, encrypted_private_key):
    init_vector = bytes.fromhex(public_key[:32])
    cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC, init_vector)
    private_key = cipher.decrypt(bytes.fromhex(encrypted_private_key))
    return private_key


def hash_password(password):
    return bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())


def get_time():
    dts = datetime.datetime.now(datetime.timezone.utc)
    return round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)


def generate_auth_token(secret_key, public_key):
    serializer = Serializer(secret_key)
    token = serializer.dumps({'public_key': public_key})
    return token.decode('ascii')


def deserialize_auth_token(secret_key, token):
    serializer = Serializer(secret_key)
    return serializer.loads(token)

# Transferência de sensores desativada.
# async def transfer_sensor(self, request):
#     private_key = await self._authorize(request)

#     body = await decode_request(request)
#     required_fields = ['receiving_user']
#     validate_fields(required_fields, body)

#     sensor_id = request.match_info.get('sensor_id', '')

#     await self._messenger.send_transfer_sensor_transaction(
#         private_key=private_key,
#         receiving_user=body['receiving_user'],
#         sensor_id=sensor_id,
#         timestamp=get_time())

#     return json_response(
#         {'data': 'Transfer sensor transaction submitted'})

# Antigo sensor update
# async def update_sensor(self, request):
#     private_key = await self._authorize(request)

#     body = await decode_request(request)
#     required_fields = ['latitude', 'longitude', 'measurement']
#     validate_fields(required_fields, body)

#     sensor_id = request.match_info.get('sensor_id', '')

#     await self._messenger.send_update_sensor_transaction(
#         private_key=private_key,
#         latitude=body['latitude'],
#         longitude=body['longitude'],
#         measurement=body['measurement'],
#         sensor_id=sensor_id,
#         timestamp=get_time())

#     return json_response(
#         {'data': 'Update sensor transaction submitted'})