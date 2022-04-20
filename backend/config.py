from os import environ
from dotenv import load_dotenv


load_dotenv('.env')
#SECRET_KEY = environ.get('TWITTER_BEARER_TOKEN')

class TwitterAPI:
    TWITTER_BEARER_TOKEN = environ.get('TWITTER_BEARER_TOKEN')
    DB_URL = environ.get('DB_URL')

class ConnectDB:
    DB_URL = environ.get('DB_URL')
    USERNAME = environ.get('DB_USERNAME')
    PASSWORD = environ.get('DB_PASSWORD')