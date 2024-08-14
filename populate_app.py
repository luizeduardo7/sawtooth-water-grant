import requests
import jwt
import base64
import json
import random
import pandas as pd
from faker import Faker

fake = Faker("pt_BR")
base_url = "http://localhost:8000"
FLOAT_PRECISION = 1000000

def to_int(num):
    return int(float(num) * FLOAT_PRECISION)

def create_name_username():
    name = fake.name()
    username = name.lower().replace(" ", "_")
    return name, username

def treat_name_username(name):
    name = name.lower().title()
    name_parts = name.split()
    first_names = name_parts[:2]
    username = "_".join(first_names).lower()
    return name, username

def get_public_key(token):
    if not token:
        return None

    content = token.split('.')[1]
    content += '=' * (-len(content) % 4) # Adiciona padding
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

def make_request_create_user(name, bearer_token):
    headers = make_header(bearer_token)

    user = treat_name_username(name)
    data = {
        "name": user[0],
        "username": user[1],
        "password": "1234",
	    "created_by_admin_public_key": get_public_key(bearer_token)  
    }
    
    return headers, data

def make_request_create_sensor(user_bearer_token, sensor_id, lat, long):
    headers = make_header(user_bearer_token)
    
    data = {
        "sensor_id": str(sensor_id),
        "latitude": to_int(lat),
        "longitude": to_int(long)
    }
    
    return headers, data

def make_request_update_user_quota(user_bearer_token, admin_bearer_token, quota):
    headers = make_header(user_bearer_token)

    data = {
        "user_public_key": get_public_key(user_bearer_token),
        "quota": quota,
	    "updated_by_admin_public_key": get_public_key(admin_bearer_token)  
    }
    
    return headers, data


# ----------------------------------------------Main-----------------------------------------------------------------------------


def main():

    # ------ Autenticação de admin ------

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
        "name": "João Ademir Neto",
        "password": "1234"
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/2023.5.8",
        "Authorization": "Bearer " + response.json()['authorization'] 
    }

    # Faz uma requisição POST para criar um novo administrador chamado "João Ademir Neto"
    admin_response = requests.request("POST", url, json=payload, headers=headers)
    admin_token = admin_response.json()['authorization']

    # ------ Criação de usuários e sensores ------

    # URL para criar um novo usuário
    create_user_url = base_url + "/users"

    # URL para criar um novo sensor
    create_sensor_url = base_url + "/sensors"

    # Leitura do arquivo CSV
    df = pd.read_csv("outorgas_ANA_10_amostras.csv")

    # ID icremental para sensores
    sensor_id = 1

    # Iteração sobre as linhas do arquivo CSV
    for index, row in df.iterrows():
        name = row['Nome_do_Requerente']
        latitude = row['Latitude'].replace(',','.')
        longitude = row['Longitude'].replace(',','.')
        monthly_quota = int(row['VolumeAnual_mÂ³']/12)  

        print(f"Linha {index}:")
        print(f"  Nome do Requerente: {name}")
        print(f"  Localização: {latitude}, {longitude}")
        print(f"  Volume Anual: {monthly_quota} m³")

        response = make_request(create_user_url, 
                                make_request_create_user(name, admin_token))
        
        user_token = response.json()['authorization']

        # ------ Atualização de quota de usuário ------
        update_user_url = base_url + "/users/" + get_public_key(user_token) +"/update"
        make_request(update_user_url,
                    make_request_update_user_quota(user_token,
                                                    admin_token,
                                                    monthly_quota))
        
        # ------ Criação de sensor ------
        make_request(create_sensor_url, 
                    make_request_create_sensor(user_token,
                                                sensor_id,
                                                latitude,
                                                longitude))
        
        # ------ Atualização de sensor ------
        # update_sensor_url = base_url + "/sensors/" + str(sensor_id) + "/update"


        # Incrementa o ID do sensor
        sensor_id += 1
        
        # print(response.status_code)
        # print(response.json())
        # print(response.json()['authorization'])
        
if __name__ == "__main__":
    main()