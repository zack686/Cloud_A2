import couchdb


user = "admin"
password = "pass123"
couchserver = couchdb.Server("http://%s:%s@172.26.131.127:5984/" % (user, password))

for dbname in couchserver:
    print(dbname)