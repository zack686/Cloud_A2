from apis import app
from config import TwitterAPI
from tweepy import Client

# from apispec import APISpec
# from apispec.ext.marshmallow import MarshmallowPlugin
# from apispec_webframeworks.flask import FlaskPlugin
# from flask import Flask, jsonify, render_template, send_from_directory
# from marshmallow import Schema, fields
from flask import Flask
from flask_restx import Resource, Api

api = Api(app)

@app.route("/")
def index():
    return "Cloud A2"

@api.route("/cloud")
class Cloud(Resource):
    def get(self):
        return "Cloud A2"

@api.route("/search")
class TwitterSeach(Resource):
    def get(self):

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
        
        return tweets

# @app.route("/search")
# def twetterSearch():

#     bearer_token = app.config["TWITTER_BEARER_TOKEN"]

#     if not bearer_token:
#         raise RuntimeError("Not found bearer token")
    
#     client = Client(bearer_token)

#     # https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
#     query = "melbourne"

#     max_results = 10
#     limit = 30
#     counter = 0
#     tweets = {}

#     # https://docs.tweepy.org/en/stable/client.html#search-tweets
#     resp = client.search_recent_tweets(query, max_results=max_results)
#     if resp.errors:
#         raise RuntimeError(resp.errors)
#     if resp.data:
#         for tweet in resp.data:
#             print(tweet.__repr__())
#             tweets[counter] = tweet.__repr__()
#             counter += 1
    
#     # while resp.meta["next_token"] and counter < limit:
#     #     resp = client.search_recent_tweets(query, max_results=max_results, next_token=resp.meta["next_token"])
#     #     if resp.errors:
#     #         raise RuntimeError(resp.errors)
#     #     if resp.data:
#     #         for tweet in resp.data:
#     #             print(tweet.__repr__())
#     #            # tweets += tweet.__repr__()
#     #             tweets[counter] = tweet.__repr__()
#     #             counter += 1
#     return tweets