import tweepy
# Subclass Stream to print IDs of Tweets received
consumer_key = "3bYkLieVfNVSsez3IE0U84JwH"
consumer_secret = "FA0GQQy2OKRRfQi7Oej7QpDKAnTXvDGZDBD5F10ra5WyH1EOp6"
access_token = "1514846543748079616-YIPxVajLpxK8Bw8t9I5lYeR4AJ44Qe"
access_token_secret = "EjTFLMHeG0aEUPLxW3PdDFs9AgayZwx85OnbGuWLgn8Vg"

class IDPrinter(tweepy.Stream):

    def on_status(self, status):
        print(status)

# Initialize instance of the subclass
printer = IDPrinter(
  consumer_key, consumer_secret,
  access_token, access_token_secret
)

# Filter realtime Tweets by keyword
printer.filter(track=["Twitter"])