import time
import json
from typing import Counter

import couchdb
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
        def __init__(self):
            global reconnect
            self.reconnect = False
            global counter
            self.counter = 0
            self.api = connect_to_twitter(consumer_key, consumer_secret, access_token, access_token_secret)
        def on_data(self, data):
            tweet = json.loads(data)
            put_tweet(db, tweet)
            
            # Get user's tweets from their timeline
            for user_timeline_tweet in tweepy.Cursor(self.api.user_timeline, count=100, user_id=tweet["id"], tweet_mode="extended", exclude_replies=True, include_rts=False).items():
                tweet = json.dumps(user_timeline_tweet._json) 
                put_tweet(db, tweet)
            
            return True

        def on_error(self, status):
            if status == 420:
                return False
            elif status >= 500 and status < 600:
                self.restart = True
                return False
            else:
                return True

    stream = CustomListener(consumer_key, consumer_secret, access_token, access_token_secret)
    stream.filter(locations=[143.967590, -38.354580, 146.004181, -37.434522], languages=["en"])
    
    # Handling 5xx error
    while reconnect == True:
        counter += 1
        time.sleep(60*counter)
        collect_streamed_tweets_melbourne(db, consumer_key, consumer_secret, access_token, access_token_secret)
