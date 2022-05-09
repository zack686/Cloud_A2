from typing import List

import couchdb


def connect_to_couchdb_server(username: str, password: str, ip_address: str) -> couchdb.Server:
    """ Returns a connection to a given couchdb server. """

    return couchdb.Server(f"http://{username}:{password}@{ip_address}:5984/")


def get_tweets_in_range(db: couchdb.Database, start: str, end: str, prefix="geo") -> couchdb.client.ViewResults:
    """ Returns the documents within a database within a specified id range. A
    default partition key of `geo` is used, but other parition keyscan be
    provided. """

    startkey = f"{prefix}:{start}"
    endkey = f"{prefix}:{end}"
    return db.view("_all_docs", include_docs=True, startkey=startkey, endkey=endkey)


def bulk_put_tweets(db: couchdb.Database, tweet_list: List[dict]) -> List[tuple]:
    """ Put multiple tweets in a couchdb database, ignoring tweets with an id
    already existing in the database. Returns a list of tuples consisting of
    the document id and revision number of every tweet that was inserted into
    the database. """

    output = db.update(tweet_list)
    return [(doc_id, doc_rev) for (success, doc_id, doc_rev) in output if success]