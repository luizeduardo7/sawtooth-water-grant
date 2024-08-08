import requests
import jwt
import base64
import json
import random
from faker import Faker

fake = Faker("pt_BR")
base_url = "http://localhost:8000"

def create_name_username():
    name = fake.name()
    username = name.lower().replace(" ", "_")
    return name, username

def get_public_key(token):
    if not token:
        return None

    content = token.split('.')[1]
    content += '=' * (-len(content) % 4)  # Pad Base64 string
    decoded_content = base64.b64decode(content)
    public_key = json.loads(decoded_content)['public_key']

    return public_key

def make_header(token):
    return {
        'Authorization': "Bearer" + token,
        'Content-Type': 'application/json'
    }

def make_request(url, params):
    headers, data = params
    response =  requests.post(url, headers=headers, json=data)
    return response

def make_request_create_admin(bearer_token):
    headers = make_header(bearer_token)

    data = {
        "username": fake.user_name(),
        "name": fake.name(),
        "password": "12345"
    }
    
    return headers, data

def make_request_create_user(bearer_token):
    headers = make_header(bearer_token)

    user = create_name_username()
    data = {
        "username": user[1],
        "name": user[0],
        "password": "12345",
	    "created_by_admin_public_key": get_public_key(bearer_token)  
    }
    
    return headers, data

def make_request_update_user_quota(user_bearer_token, admin_bearer_token):
    headers = make_header(user_bearer_token)

    data = {
        "user_public_key": get_public_key(user_bearer_token),
        "quota": random.randint(50, 1000),
	    "updated_by_admin_public_key": get_public_key(admin_bearer_token)  
    }
    
    return headers, data

url = "http://127.0.0.1:8000/authentication"

payload = {
    "username": "admin",
    "password": "feagharegfrahbgr"
}
headers = {
    "Content-Type": "application/json",
    "User-Agent": "insomnia/2023.5.8"
}

# Faz uma requisição POST para autenticar o usuário "admin"
response = requests.request("POST", url, json=payload, headers=headers)

# ------ Criação de admin ------

url = "http://127.0.0.1:8000/admins"

payload = {
    "username": "joao_ademir",
    "name": "João Ademir",
    "password": "12345"
}
headers = {
    "Content-Type": "application/json",
    "User-Agent": "insomnia/2023.5.8",
    "Authorization": "Bearer " + response.json()['authorization'] 
}

# Faz uma requisição POST para criar um novo administrador chamado "João Ademir"
admin_response = requests.request("POST", url, json=payload, headers=headers)
admin_token = admin_response.json()['authorization']


# ------ Criação de usuários e sensores ------

create_user_url = base_url + "/users"

for i in range(5):
    response = make_request(create_user_url, make_request_create_user(admin_token))

    user_token = response.json()['authorization']
    update_user_url = base_url + "/users/" + get_public_key(user_token) +"/update"

    # ------ Atualização de quota de usuário ------
    make_request(update_user_url, make_request_update_user_quota(user_token, admin_token))
    
    
    # print(response.status_code)
    # print(response.json())
    # print(response.json()['authorization'])
