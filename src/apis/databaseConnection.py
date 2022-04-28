import couchdb
from typing import List
import uuid


def connect_to_database(username: str, password: str, ip_address: str, dbname: str) -> couchdb.Database:
    """ Returns a connection to a given couchdb database. """
    server = couchdb.Server(f"http://{username}:{password}@{ip_address}:5984/")
    return server[dbname]


def put_doc(db: couchdb.Database, doc: dict) -> tuple:
    """ Put one document in a couchdb database, doing nothing if there is
    already a document in the database with the given id. In the case of a
    successful put, returns a tuple consisting of the document id and revision
    number. """
    if "_id" not in doc:
        doc["_id"] = doc.get("id", uuid.uuid4())

    try:
        return db.save(doc)
    except couchdb.http.ResourceConflict:
        return


def bulk_put_docs(db: couchdb.Database, doc_list: List[dict]) -> List[tuple]:
    """ Put multiple documents in a couchdb database, ignoring documents with
    an id already existing in the database. Returns a list of tuples consisting
    of the document id and revision number of every document that was inserted
    into the database. """
    for doc in doc_list:
        if "_id" not in doc:
            doc["_id"] = doc.get("id", uuid.uuid4())

    output = db.update(doc_list)
    return [(doc_id, doc_rev) for (success, doc_id, doc_rev) in output if success]


if __name__ == "__main__":
    db = connect_to_database("admin", "password", "172.26.130.11", "twitter")
    docs = [{"_id":"1","test":1}, {"_id":"2","test":2}]
    output = bulk_put_docs(db, docs)
    if output is not None:
        print(output)