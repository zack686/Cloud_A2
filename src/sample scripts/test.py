import tweepy

consumer_key = "PUS4Ig5X5uDocHt8jYsH1qlhG"
consumer_secret = "SB0qgJ9RZXMF0rBNBHQWJU8a7yhu5wpOmk6cOA0STZ2szQQtOh"
access_token = "1280364427112415239-fBTXfzWk3d8REDeefnhyjXBWYt1ZMa"
access_token_secret = "aexPP1RpX70z3gzlRmCUOOKoUTafykEh19Ud1cYIsU68j"

# Subclass Stream to print IDs of Tweets received
class IDPrinter(tweepy.Stream):

    def on_status(self, status):
        print(status.id)

# Initialize instance of the subclass
printer = IDPrinter(
  consumer_key, consumer_secret,
  access_token, access_token_secret
)

# Filter realtime Tweets by keyword
printer.filter(track=["Twitter"])