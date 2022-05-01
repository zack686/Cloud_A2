from multiprocessing.sharedctypes import Value
import tweepy


consumer_key = "UG5SdYVvFUllQjGmbaujH1sjE"
consumer_secret = "ZNTk1vEgLplByLIosOkJo7011a4OeTR9yeQsnS5hUFLawQnYsx"
access_token = "1514846543748079616-YIPxVajLpxK8Bw8t9I5lYeR4AJ44Qe"
access_token_secret = "EjTFLMHeG0aEUPLxW3PdDFs9AgayZwx85OnbGuWLgn8Vg"

import json
from tweepy import StreamingClient, StreamRule, Tweet


auth = tweepy.OAuth1UserHandler(
   consumer_key, consumer_secret, access_token, access_token_secret
)

api = tweepy.API(auth, wait_on_rate_limit=True)

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
        pass
    
    def on_data(self, raw_data):
        data = json.loads(raw_data)
        print(data)

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
        client.filter(expansions="geo.place_id")
        
    except KeyboardInterrupt:
        client.disconnect()
