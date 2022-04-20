import couchdb


user = "admin"
password = "pass123"
couchserver = couchdb.Server("http://%s:%s@172.26.134.2:5984/" % (user, password))

for dbname in couchserver:
    print(dbname)