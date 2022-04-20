from os import environ
from dotenv import load_dotenv


load_dotenv('.env')
#SECRET_KEY = environ.get('TWITTER_BEARER_TOKEN')

class TwitterAPI:
    TWITTER_BEARER_TOKEN = environ.get('TWITTER_BEARER_TOKEN')

#class TwitterAPI:
#    TWITTER_BEARER_TOKEN = environ.get('AAAAAAAAAAAAAAAAAAAAAJspbgEAAAAADFM%2BOs5zS8ib9LHFvzGw8byssBg%3DoFHQ4m8azb9ba0vs6KcZ41joi0NS42daexGqziCdS3RlZ3fDjj')
