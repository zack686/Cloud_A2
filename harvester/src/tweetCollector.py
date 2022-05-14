import json
from typing import List

import couchdb
import tweepy

from .couchDB import put_tweet, bulk_put_tweets

    
def connect_to_twitter(consumer_key: str, consumer_secret: str, access_token: str,
    access_token_secret: str) -> tweepy.API:
    """ Returns a connection to the twitter search API. """

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, access_token, access_token_secret) 
    api = tweepy.API(auth, wait_on_rate_limit=True)
    api.verify_credentials()

    return api


def collect_streamed_tweets(server: couchdb.Server, consumer_key: str,
    consumer_secret: str, access_token: str, access_token_secret: str,
    bounding_box: List[float]):
    """ Connect to the twitter streaming API, and collect tweets found within a
    bounding box, written in English, into the twitter database of the given
    couchDB server. Additionally, load the 100 most recent tweets from each
    user with a tweet collected by the streamer. """

    class CustomListener(tweepy.Stream):
        def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
            self.search_api = connect_to_twitter(
                consumer_key,
                consumer_secret,
                access_token,
                access_token_secret
            )
            super().__init__(
                consumer_key,
                consumer_secret,
                access_token,
                access_token_secret
            )

        def on_data(self, data):
            # Load the current tweet and insert into the database
            tweet = json.loads(data)
            put_tweet(server, tweet)

            # Load the user's tweet history as well
            tweet_history = self.search_api.user_timeline(
                user_id=tweet["user"]["id"],
                count=100,
                include_rts=False,
                tweet_mode="extended"
            )
            tweet_history = [tweet._json for tweet in tweet_history]
            bulk_put_tweets(server, tweet_history)

            return True  # Resume harvesting

        def on_error(self, status):
            if (status >= 500 and status < 600) or status == 420:
                return False  # Retry - tweepy will handle any back-off internally
            else:
                return True  # Stop execution

    stream = CustomListener(consumer_key, consumer_secret, access_token, access_token_secret)
    stream.filter(track=[ "vce", "vcaa", "year11" "year12", "school", "atar", "units 3/4"], locations=bounding_box, languages=["en"])