import os

class Config:
    SAWTOOTH_REST_API_URL = os.getenv('SAWTOOTH_REST_API_URL', 'http://rest-api:8008')
