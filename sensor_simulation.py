import requests
import random
import time

# Função para simular atualizações do sensor
def simulate_sensor_update(sensor_id, token):
    # Gerar valor de medição aleatório
    measurement =  round(random.uniform(0, 10000),2)
    
    # Preparar os dados da solicitação
    payload = {
        'measurement': measurement
    }
    
    # Definir os cabeçalhos com o token de autorização
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Enviar a solicitação POST para atualizar os dados do sensor
    response = requests.post(f'http://127.0.0.1:8000/sensors/{sensor_id}/update', json=payload, headers=headers)
    
    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200:
        print(f'Atualização do sensor de ID  {sensor_id} bem-sucedida.')
    else:
        print(f'Falha na atualização do sensor com código de status {response.status_code}: {response.text}')

# Definir o ID do sensor e o token de autorização
sensor_id = 1
authorization_token = 'eyJhbGciOiJIUzUxMiIsImlhdCI6MTcxMDQ0NjM4NCwiZXhwIjoxNzEwNDQ5OTg0fQ.eyJwdWJsaWNfa2V5IjoiMDJiNjNiYzU4MTAzZjkwOGY5ZDY2M2Q5NGZjMjU2YTgyZDk5NzNhYTNhNDJhM2Q4YWRjMTIzNTFiYTUzYzYzNTc1In0.VglXz7XiDs0yHNGJiYMObJav0m50g_4RifY9LGmycluYYqWm3a_HpTZmwq5HoG7dYDkQJf7z-AG092-Xb-ZH4w'

# Simular atualizações do sensor a cada cinco segundos
while True:
    simulate_sensor_update(sensor_id, authorization_token)
    time.sleep(5)