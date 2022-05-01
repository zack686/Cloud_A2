import tweepy
import json
bearer_token = "AAAAAAAAAAAAAAAAAAAAAEsNbgEAAAAA1X6WSK4PEKbw82NXCWGKCgD%2Bjt4%3DjXHskBEH0Fbt2ipcW79cwjZ1ScACNLrz6kTeCHylMkyn2b6Aks"

client = tweepy.Client(bearer_token=bearer_token)

# Replace with your own search query
# query = 'covid -is:retweet place_country:US'

query = 'covid -is:retweet'

# tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
#                                      user_fields=['profile_image_url'], expansions='author_id', max_results=100)
consumer_key = "3bYkLieVfNVSsez3IE0U84JwH"
consumer_secret = "FA0GQQy2OKRRfQi7Oej7QpDKAnTXvDGZDBD5F10ra5WyH1EOp6"
access_token = "1514846543748079616-YIPxVajLpxK8Bw8t9I5lYeR4AJ44Qe"
access_token_secret = "EjTFLMHeG0aEUPLxW3PdDFs9AgayZwx85OnbGuWLgn8Vg"


auth = tweepy.OAuth1UserHandler(
   consumer_key, consumer_secret, access_token, access_token_secret
)

api = tweepy.API(auth, wait_on_rate_limit=True)

number_of_items = 2
for tweet in tweepy.Cursor(api.search_tweets, q="Melbourne", count=1, tweet_mode='extended').items(number_of_items):
    text = tweet._json["full_text"]
    
    # print(text)
    # print('\n\n')
    print(tweet)
# Get users list from the includes object
# users = {u["id"]: u for u in tweets.includes['users']}

# for tweet in tweets.data:
#     if users[tweet.author_id]:
#         user = users[tweet.author_id]
        
        # print(user.profile_image_url)