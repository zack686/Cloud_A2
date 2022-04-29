import tweepy

bearer_token = "AAAAAAAAAAAAAAAAAAAAAEsNbgEAAAAA1X6WSK4PEKbw82NXCWGKCgD%2Bjt4%3DjXHskBEH0Fbt2ipcW79cwjZ1ScACNLrz6kTeCHylMkyn2b6Aks"

client = tweepy.Client(bearer_token=bearer_token)

# Replace with your own search query
# query = 'covid -is:retweet place_country:US'

query = 'covid -is:retweet'

# tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
#                                      user_fields=['profile_image_url'], expansions='author_id', max_results=100)
consumer_key = "3bYkLieVfNVSsez3IE0U84JwH"
consumer_secret = "FA0GQQy2OKRRfQi7Oej7QpDKAnTXvDGZDBD5F10ra5WyH1EOp6"
access_token = "1514846543748079616-0lUyVyqtSFUet7yksU1jlViBbidR4k"
access_token_secret = "z0G87ZZTpLUSvRVnv04sCMl4OSNl3Shw7FT4hKJMX0b34"


auth = tweepy.OAuth1UserHandler(
   consumer_key, consumer_secret, access_token, access_token_secret
)

api = tweepy.API(auth, wait_on_rate_limit=True)


for tweet in tweepy.Cursor(api.search_tweets, q="Melbourne", count=10, tweet_mode='extended').items():
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