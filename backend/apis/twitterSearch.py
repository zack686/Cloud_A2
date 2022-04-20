from apis import app
from config import TwitterAPI, ConnectDB
from flask import Flask
from flask_restx import Resource, Api
import couchdb
from tweepy import Client



api = Api(app, doc='/docs', title='Api documentation for Cloud A2')

@app.route("/")
def index():
    return "Cloud A2"

@api.route("/search")
class TwitterSeach(Resource):
    def get(self):
        '''Get 10 tweets from Melbourne'''
        
        bearer_token = TwitterAPI.TWITTER_BEARER_TOKEN

        if not bearer_token:
            raise RuntimeError("Not found bearer token")
        
        client = Client(bearer_token)

        # https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
        query = "melbourne"

        max_results = 10
        limit = 30
        counter = 0
        tweets = {}

        # https://docs.tweepy.org/en/stable/client.html#search-tweets
        resp = client.search_recent_tweets(query, max_results=max_results)
        if resp.errors:
            raise RuntimeError(resp.errors)
        if resp.data:
            for tweet in resp.data:
                print(tweet.__repr__())
                tweets[counter] = tweet.__repr__()
                counter += 1
        
        # while resp.meta["next_token"] and counter < limit:
        #     resp = client.search_recent_tweets(query, max_results=max_results, next_token=resp.meta["next_token"])
        #     if resp.errors:
        #         raise RuntimeError(resp.errors)
        #     if resp.data:
        #         for tweet in resp.data:
        #             print(tweet.__repr__())
        #            # tweets += tweet.__repr__()
        #             tweets[counter] = tweet.__repr__()
        #             counter += 1

        return tweets

# The class is just a simple example to access the DB
@api.route("/crud")
class CRUDExample(Resource):
    def get(self):
        ConnectDB
        url = ConnectDB.DB_URL
        user = ConnectDB.USERNAME
        password = ConnectDB.PASSWORD
        names = {}
        
        # connect to the db server
        couchserver = couchdb.Server(url % (user, password))
        
        for num, dbname in enumerate(couchserver):
            print(dbname)
            names[num] = dbname 
            
        return names