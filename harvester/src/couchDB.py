from typing import List
import uuid

import couchdb


def connect_to_couchdb_server(username: str, password: str, ip_address: str) -> couchdb.Server:
    """ Returns a connection to a given couchdb server. """

    return couchdb.Server(f"http://{username}:{password}@{ip_address}:5984/")


def set_tweet_id(tweet: dict):
    """ Set the couchdb id of a tweet in-place (overwriting any existing '_id'
    key), as a combination of the geo partition key and the tweet id. """

    geo = "geo" if tweet.get("geo", None) is not None else "non-geo"
    if "id_str" in tweet:
        tweet["_id"] = geo + ":" + tweet.get("id_str")
    elif "id" in tweet:
        id = str(tweet.get("id"))
        tweet["id_str"] = id
        tweet["_id"] = geo + ":" + id
    else:
        tweet["_id"] = geo + ":" + str(uuid.uuid4())
        tweet["unidentified"] = True


def transform_extracted_tweets(tweet_list: List[dict]):
    """ When tweets are extracted from some couchdb database they will not
    necessarily the required form for insertion. This method transforms a list
    of tweets in-place by unnesting extracted tweets, ensuring that a
    partitioned key is set, and removing the revision number key. """

    for (i, tweet) in enumerate(tweet_list):
        if "doc" in tweet:
            tweet = tweet["doc"]
            tweet.pop("_rev", None)
            set_tweet_id(tweet)
        tweet_list[i] = tweet


def put_tweet(server: couchdb.Server, tweet: dict, allow_unidentified: bool=False) -> tuple:
    """ Put one tweet in the 'twitter' database of a given couchdb server,
    doing nothing if there is already a tweet in the database with the given
    id. In the case of a successful put, returns a tuple consisting of the
    document id and revision number.
    
    Tweets with no 'id' or 'id_str' key are assigned a random UUID if
    `allow_unidentified` is set to true and rejected otherwise. """

    set_tweet_id(tweet)
    if "unidentified" in tweet and not allow_unidentified:
        return

    try:
        return server["twitter"].save(tweet)
    except couchdb.http.ResourceConflict:
        return


def bulk_put_tweets(server: couchdb.Server, tweet_list: List[dict],
    allow_unidentified: bool=False) -> List[tuple]:
    """ Put multiple tweets in the 'twitter' database of a given couchdb
    server, ignoring tweets with an id already existing in the database.
    Returns a list of tuples consisting of the document id and revision number
    of every tweet that was inserted into the database.
    
    Tweets with no 'id' or 'id_str' key are silently rejected if
    `allow_unidentified` is set to falsee. """

    for tweet in tweet_list:
        set_tweet_id(tweet)

    if not allow_unidentified:
        tweet_list = [tweet for tweet in tweet_list if "unidentified" not in tweet]

    results = server["twitter"].update(tweet_list)
    return [(doc_id, doc_rev) for (success, doc_id, doc_rev) in results if success]
