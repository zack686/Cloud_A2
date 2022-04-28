import couchdb
import uuid


def connect_to_database(username: str, password: str, ip_address: str, dbname: str) -> couchdb.Database:
    server = couchdb.Server(f"http://{username}:{password}@{ip_address}:5984/")
    return server[dbname]


def put_doc(db: couchdb.Database, doc: dict) -> tuple:
    if "_id" not in doc:
        if "id" in doc:
            doc["_id"] = doc["id"]
        else:
            doc["_id"] = uuid.uuid4()

    try:
        return db.save(doc)
    except:
        print(f"document with id {doc['_id']} already exists - skipping")
        return


if __name__ == "__main__":
    db = connect_to_database("admin", "password", "172.26.130.11", "twitter")
    doc = {"_id":"1","test":1}
    output = put_doc(db, doc)
    if output is not None:
        print(output)