from multiprocessing.sharedctypes import Value
import tweepy


consumer_key = "UG5SdYVvFUllQjGmbaujH1sjE"
consumer_secret = "ZNTk1vEgLplByLIosOkJo7011a4OeTR9yeQsnS5hUFLawQnYsx"
access_token = "1513036168199553031-pdsr3Bip4XwELmSre9P7uck1pl3xl5"
access_token_secret = "9cOIV9rHndNov8QD4GSbjS0QUjls03KJuEhCR4bt5STnX"

# Subclass Stream to print IDs of Tweets received
class IDPrinter(tweepy.Stream):

    def on_status(self, status):
        print(status.id)

# Initialize instance of the subclass
# printer = IDPrinter(
#   consumer_key, consumer_secret,
#   access_token, access_token_secret
# )

# # Filter realtime Tweets by keyword
# printer.filter(track=["Melbourne"])

# streaming_client = tweepy.StreamingClient("AAAAAAAAAAAAAAAAAAAAAEsNbgEAAAAA1X6WSK4PEKbw82NXCWGKCgD%2Bjt4%3DjXHskBEH0Fbt2ipcW79cwjZ1ScACNLrz6kTeCHylMkyn2b6Aks")
# # streaming_client.sample()
# streaming_client.add_rules(tweepy.StreamRule("Melbourne"))
# streaming_client.filter()


import os
import logging
import json
from tweepy import StreamingClient, StreamRule, Tweet


class TweetListener(StreamingClient):
    """
    StreamingClient allows filtering and sampling of realtime Tweets using Twitter API v2.
    https://docs.tweepy.org/en/latest/streamingclient.html#tweepy.StreamingClient
    """

    def on_tweet(self, tweet):
        # print(json.load(tweet))
        # json_data = json.loads(tweet)  # convert string to JSON
        # print(json_data)
        # print(tweet.id)
        print(type(tweet))
        # print(tweet._json["created_at"])
        print(tweet.geo)
        # print(tweet)
    # def on_status(self, tweet_mode="extended"):
    #     print(data)
    
    # print full tweet data
    # def on_status(self, status):
    #     if hasattr(status, "retweeted_status"):  # Check if Retweet
    #         try:
    #             print(status.retweeted_status.extended_tweet["full_text"])
    #         except AttributeError:
    #             print(status.retweeted_status.text)
    #     else:
    #         try:
    #             print(status.extended_tweet["full_text"])
    #         except AttributeError:
    #             print(status.text)
    # def on_data(self, raw_data):
    #      # self.tweet_count += 1  # track number of tweets processed
    #     json_data = json.loads(raw_data)  # convert string to JSON
    #     # print(json_data["data"]["id"])
    #     # self.db.tweets.insert_one(json_data)  # store in tweets collection
    #     # print(json_data) 
    #     # print(f'     Created at: {json_data["created_at"]}')         
    #     # print(f'Tweets received: {self.tweet_count}')  

    def on_request_error(self, status_code):
        print(status_code)

    def on_connection_error(self):
        self.disconnect()


if __name__ == "__main__":
    """
     - Save it in a secure location
     - Treat it like a password or a set of keys
     - If security has been compromised, regenerate it
     - DO NOT store it in public places or shared docs
    """
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAEsNbgEAAAAA1X6WSK4PEKbw82NXCWGKCgD%2Bjt4%3DjXHskBEH0Fbt2ipcW79cwjZ1ScACNLrz6kTeCHylMkyn2b6Aks"

    if not bearer_token:
        raise RuntimeError("Not found bearer token")

    client = TweetListener(bearer_token)

    # https://docs.tweepy.org/en/latest/streamingclient.html#streamrule
    # https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
    # Operator availability (check the operators table)
    # - Core operators: Available when using any access level.
    # - Advanced operators: Available when using a Project with Academic Research access.
    # keyword:
    #   - "melbourne"
    rules = [
        StreamRule(value="melbourne")
    ]

    # https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules
    # Remove existing rules
    resp = client.get_rules()
    if resp and resp.data:
        rule_ids = []
        for rule in resp.data:
            rule_ids.append(rule.id)

        client.delete_rules(rule_ids)

    # Validate the rule
    resp = client.add_rules(rules, dry_run=True)
    if resp.errors:
        raise RuntimeError(resp.errors)

    # Add the rule
    resp = client.add_rules(rules)
    if resp.errors:
        raise RuntimeError(resp.errors)

    # https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream-rules
    print(client.get_rules())
    # print(client.on_tweet)
    
    # https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream
    try:
        # client.filter()
        stream = tweepy.Stream(auth=api.auth, listener=LiveTweetListener(), tweet_mode='extended')

        
    except KeyboardInterrupt:
        client.disconnect()
