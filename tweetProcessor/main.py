import os

from src.couchDB import connect_to_database_partition


db = connect_to_database_partition(
    os.environ["COUCHDB_USERNAME"],
    os.environ["COUCHDB_PASSWORD"],
    os.environ["COUCHDB_NODE_IP"],
    "twitter",
    "geo"
)
