from apis import app
from config import TwitterAPI
from tweepy import Client
from flask import Flask
from flask_restx import Resource, Api

api = Api(app, doc='/docs', title='Api documentation for Cloud A2')

@app.route("/")
def index():
    return "Cloud A2"

@api.route("/search")
class TwitterSeach(Resource):
    def get(self):
        '''Get 10 tweets from Melbourne'''
        
        bearer_token = app.config["TWITTER_BEARER_TOKEN"]

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