import couchdb
import json
import tweepy

from .couchDB import put_tweet

def connect_to_twitter(consumer_key: str, consumer_secret: str, access_token: str,
    access_token_secret: str) -> tweepy.API:
    """ Returns a connection to the twitter API. """

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, access_token, access_token_secret) 
    api = tweepy.API(auth, wait_on_rate_limit=True)

    try:
        api.verify_credentials()
    except:
        print("could not authenticate twitter credentials")
        return

    return api


def collect_streamed_tweets_melbourne(db: couchdb.Database, consumer_key: str,
    consumer_secret: str, access_token: str, access_token_secret: str):
    """ Connect to the twitter streaming API, and collect tweets found within a
    bounding box representing the majority of Greater Melbourne, written in
    English, into the given couchDB database. """

    class CustomListener(tweepy.Stream):
        def on_data(self, data):
            tweet = json.loads(data)
            put_tweet(db, tweet)
            return True

        def on_error(self, status):
            if status == 420:
                return False
            else:
                return True

    stream = CustomListener(consumer_key, consumer_secret, access_token, access_token_secret)
    stream.filter(locations=[143.967590, -38.354580, 146.004181, -37.434522], languages=["en"])