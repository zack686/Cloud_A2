import tweepy
import json

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""


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
