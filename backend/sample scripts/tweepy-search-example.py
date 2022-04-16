import os

from tweepy import Client


if __name__ == "__main__":
    """
     - Save it in a secure location
     - Treat it like a password or a set of keys
     - If security has been compromised, regenerate it
     - DO NOT store it in public places or shared docs
    """
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not bearer_token:
        raise RuntimeError("Not found bearer token")

    client = Client(bearer_token)

    # https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
    query = "melbourne"

    max_results = 10
    limit = 30
    counter = 0

    # https://docs.tweepy.org/en/stable/client.html#search-tweets
    resp = client.search_recent_tweets(query, max_results=max_results)
    if resp.errors:
        raise RuntimeError(resp.errors)
    if resp.data:
        for tweet in resp.data:
            print(tweet.__repr__())
            counter += 1

    while resp.meta["next_token"] and counter < limit:
        resp = client.search_recent_tweets(query, max_results=max_results, next_token=resp.meta["next_token"])
        if resp.errors:
            raise RuntimeError(resp.errors)
        if resp.data:
            for tweet in resp.data:
                print(tweet.__repr__())
                counter += 1
