import os

from src.couchDB import connect_to_couchdb_server
from src.tweetCollector import collect_streamed_tweets


server = connect_to_couchdb_server(
    os.environ["COUCHDB_USERNAME"],
    os.environ["COUCHDB_PASSWORD"],
    os.environ["COUCHDB_NODE_IP"],
)
collect_streamed_tweets(
    server,
    os.environ["TWITTER_API_KEY"],
    os.environ["TWITTER_API_KEY_SECRET"],
    os.environ["TWITTER_ACCESS_TOKEN"],
    os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
    [143.967590, -38.354580, 146.004181, -37.434522]
)
