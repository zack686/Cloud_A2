import tweepy
import json
# Subclass Stream to print IDs of Tweets received
consumer_key = "3bYkLieVfNVSsez3IE0U84JwH"
consumer_secret = "FA0GQQy2OKRRfQi7Oej7QpDKAnTXvDGZDBD5F10ra5WyH1EOp6"
access_token = "1514846543748079616-YIPxVajLpxK8Bw8t9I5lYeR4AJ44Qe"
access_token_secret = "EjTFLMHeG0aEUPLxW3PdDFs9AgayZwx85OnbGuWLgn8Vg"

class Stream(tweepy.Stream):
  def on_data(self, raw_data):
    print(json.loads(raw_data))
    
  def on_request_error(self, status_code):
        print(status_code)

  def on_connection_error(self):
        self.disconnect()

# Initialize instance of the subclass
steam = Stream(
  consumer_key, consumer_secret,
  access_token, access_token_secret
)

# Filter realtime Tweets by keyword
# Can use locations to track tweets via locations= 
# https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/basic-stream-parameters
keywords = ["Melbourne"]

steam.filter(track=keywords, locations=[143.967590, -38.354580, 146.004181, -37.434522],languages=["en"])
