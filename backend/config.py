from os import environ
from dotenv import load_dotenv


load_dotenv('.env')
#SECRET_KEY = environ.get('TWITTER_BEARER_TOKEN')

DEBUG=environ.get('DEBUG')
class TwitterAPI:
    TWITTER_BEARER_TOKEN = environ.get('TWITTER_BEARER_TOKEN')