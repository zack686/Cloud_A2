import os

from src.couchDB import connect_to_database
from src.tweetCollector import collect_streamed_tweets_melbourne


db = connect_to_database(
    os.environ["COUCHDB_USERNAME"],
    os.environ["COUCHDB_PASSWORD"],
    os.environ["COUCHDB_NODE_IP"],
    "twitter"
)
collect_streamed_tweets_melbourne(
    db,
    os.environ["TWITTER_API_KEY"],
    os.environ["TWITTER_API_KEY_SECRET"],
    os.environ["TWITTER_ACCESS_TOKEN"],
    os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
)
