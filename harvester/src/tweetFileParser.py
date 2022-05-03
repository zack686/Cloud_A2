import concurrent.futures
import json
from typing import Tuple

import couchdb

from .couchDB import transform_extracted_tweets, bulk_put_tweets


def process_tweet_file_chunk(db: couchdb.Database, file_path: str, start_end_bytes: Tuple[int, int]) -> int:
    """ Given a JSON file of tweets extracted from couchDB, process the tweets
    into the given database, starting from a given byte in a file, and ending
    at the nearest line end after a specified end-byte. """

    start_byte = start_end_bytes[0]
    end_byte = start_end_bytes[1]

    tweet_list = []

    with open(file_path, "rb") as f:

        # Seek to the specified start byte and skip the remainder of that line,
        # which is either the no-tweet-containing first line, or a line that
        # will be handled by another process
        f.seek(start_byte)
        f.readline()

        # Read through each line in the file segment, adding to the tweet list
        while f.tell() <= end_byte:
            line = f.readline()
            if line == b"":  # EOF is marked by an empty line
                break

            try:
                tweet = json.loads(line[:-3])  # Strip trailing b',\r\n'
            except:
                try:
                    tweet = json.loads(line[:-2])  # Last tweet has trailing b'\r\n'
                except:
                    continue

            tweet_list.append(tweet)

    # Reformat the tweets and insert into the couchdb database
    transform_extracted_tweets(tweet_list)
    output = bulk_put_tweets(db, tweet_list)
    return len(output)


def process_tweet_file(db: couchdb.Database, file_path: str):
    """ Given a JSON file of tweets extracted from couchDB, process all of the
    tweets into the given database in ~10MB chunks. """

    # Split the file into 10MB chunks
    with open(file_path, "rb") as f:
        file_size = f.seek(0, 2)

    file_chunks = []
    end_byte = 0
    while end_byte < file_size:
        start_byte = end_byte
        end_byte += 10000000
        file_chunks.append((start_byte, end_byte))
    file_chunks[-1] = (file_chunks[-1][0], file_size)

    # Use a thread pool to insert the tweets in each of the file chunks into
    # the database
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(process_tweet_file_chunk, db, file_path, chunk)
            for chunk in file_chunks
        ]
        for future in concurrent.futures.as_completed(futures):
            num_tweets_inserted = future.result()
            print(f"Inserted {num_tweets_inserted} tweets into the database.")
