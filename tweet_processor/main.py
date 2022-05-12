import os

import flair

from src.couchDB import *
from src.tweetTagger import *

# Connect to the couchdb server
server = connect_to_couchdb_server(
    os.environ["COUCHDB_USERNAME"],
    os.environ["COUCHDB_PASSWORD"],
    os.environ["COUCHDB_NODE_IP"]
)

# Get the aurin suburb boundary data
aurin_db = server["aurin"]
vic_suburbs = dict(aurin_db.get("vic_states"))

vic_suburb_boundaries = GeoBoundaries(vic_suburbs, "vic_loca_2")

# Load the flair sentiment classifier
classifier = flair.models.TextClassifier.load("en-sentiment")

# Download and tag geo-located tweets in the specified id range
insert_db = server["tagged"]
extract_db = server["twitter"]
batch_size = 500
tagged_tweets = []
tweet_generator = batch_get_tweets_with_prefix(extract_db, batch_size)

for tweet in tweet_generator:
    if len(tagged_tweets) >= batch_size:
        output = bulk_put_tweets(insert_db, tagged_tweets)
        print(output)
        print(f"Inserted {len(output)} tweets into the database.")
        tagged_tweets = []

    tagged_tweet = tag_tweet(tweet, vic_suburb_boundaries, classifier)
    if tagged_tweet is not None:
        tagged_tweets.append(tagged_tweet)

if tagged_tweets != []:
    output = bulk_put_tweets(insert_db, tagged_tweets)
    print(f"Inserted {len(output)} tweets into the database.")