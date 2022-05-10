from typing import Generator, List

import couchdb


def connect_to_couchdb_server(username: str, password: str, ip_address: str) -> couchdb.Server:
    """ Returns a connection to a given couchdb server. """

    return couchdb.Server(f"http://{username}:{password}@{ip_address}:5984/")


def batch_get_tweets_with_prefix(db: couchdb.Database, batch: int, prefix="geo") -> Generator:
    """ Returns the documents within a database within a specified id range. A
    default partition key of `geo` is used, but other parition keyscan be
    provided. """

    startkey = f"{prefix}:"
    endkey = f"{prefix}:A"
    return db.iterview("_all_docs", batch=batch, include_docs=True, startkey=startkey, endkey=endkey)


def bulk_put_tweets(db: couchdb.Database, tweet_list: List[dict]) -> List[tuple]:
    """ Put multiple tweets in a couchdb database, ignoring tweets with an id
    already existing in the database. Returns a list of tuples consisting of
    the document id and revision number of every tweet that was inserted into
    the database. """

    output = db.update(tweet_list)
    return [(doc_id, doc_rev) for (success, doc_id, doc_rev) in output if success]