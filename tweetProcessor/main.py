import os

from src.couchDB import connect_to_database

# Get the aurin suburb boundary data
db = connect_to_database(
    os.environ["COUCHDB_USERNAME"],
    os.environ["COUCHDB_PASSWORD"],
    os.environ["COUCHDB_NODE_IP"],
    "aurin",
)
