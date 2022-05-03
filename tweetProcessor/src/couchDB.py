import couchdb


def connect_to_database_partition(username: str, password: str, ip_address: str,
    dbname: str, partition: str) -> couchdb.Database:
    """ Returns a connection to a partition of a given couchdb database. """

    partitions = couchdb.Server(f"http://{username}:{password}@{ip_address}:5984/{dbname}/_partition/")
    return partitions[partition]
