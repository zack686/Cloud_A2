import concurrent.futures
import os

import flair

from src.couchDB import connect_to_couchdb_server
from src.tweetTagger import GeoBoundaries, process_tweet_range


# Connect to the couchdb cluster
server = connect_to_couchdb_server(
    os.environ["COUCHDB_USERNAME"],
    os.environ["COUCHDB_PASSWORD"],
    os.environ["COUCHDB_NODE_IP"],
    "aurin",
)

# Get the aurin suburb boundary data
aurin_db = server["aurin"]
vic_suburbs = dict(aurin_db.get("vic_states"))

vic_suburb_boundaries = GeoBoundaries(vic_suburbs, "vic_loca_2")

# Load the flair sentiment classifier
classifier = flair.models.TextClassifier.load("en-sentiment")

# Split the tweet ids into segments
id_ranges = [(str(i).zfill(2), str(i+1).zfill(2)) for i in range(100)]
id_ranges[-1] = (id_ranges[-1][0], "A")

# Use a thread pool to insert the tweets in each of the file chunks into
# the database
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = [
        executor.submit(
            process_tweet_range,
            server["twitter"],
            server["tagged"],
            id_range,
            vic_suburb_boundaries,
            classifier
        )
        for id_range in id_ranges
    ]
    for future in concurrent.futures.as_completed(futures):
        num_tweets_inserted = future.result()
        print(f"Inserted {num_tweets_inserted} tweets into the database.")
