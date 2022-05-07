from typing import List
import uuid

import couchdb


def connect_to_database(username: str, password: str, ip_address: str, dbname: str) -> couchdb.Database:
    """ Returns a connection to a given couchdb database. """

    server = couchdb.Server(f"http://{username}:{password}@{ip_address}:5984/")
    return server[dbname]


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


def put_tweet(db: couchdb.Database, tweet: dict, allow_unidentified: bool=False) -> tuple:
    """ Put one tweet in a couchdb database (paritioned depending on whether
    the tweet is geo-enabled or not), doing nothing if there is already a
    tweet in the database with the given id. In the case of a successful put,
    returns a tuple consisting of the document id and revision number. """

    set_tweet_id(tweet)
    if "unidentified" in tweet and not allow_unidentified:
        return

    try:
        return db.save(tweet)
    except couchdb.http.ResourceConflict:
        return


def bulk_put_tweets(db: couchdb.Database, tweet_list: List[dict], allow_unidentified: bool=False) -> List[tuple]:
    """ Put multiple tweets in a couchdb database, (paritioned depending on
    whether they are geo-enabled or not), ignoring tweets with an id already
    existing in the database. Returns a list of tuples consisting of the
    document id and revision number of every tweet that was inserted into the
    database. """

    for tweet in tweet_list:
        set_tweet_id(tweet)

    if not allow_unidentified:
        tweet_list = [tweet for tweet in tweet_list if "unidentified" not in tweet]

    output = db.update(tweet_list)
    return [(doc_id, doc_rev) for (success, doc_id, doc_rev) in output if success]
