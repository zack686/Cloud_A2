from typing import Tuple

import couchdb
import flair
from shapely import geometry
from shapely.geometry  import Point

from .couchDB import get_tweets_in_range, bulk_put_tweets


class GeoBoundaries:

    def __init__(self, geojson: dict, name_field: str):
        """ Initialise the object with a name-indexed list of geographic
        area. """

        polygons = {}

        for feature in geojson["features"]:
            name = feature["properties"].get(name_field)
            polygons[name] = {
                "id": feature["id"],
                "polygon": geometry.Polygon(feature["geometry"]["coordinates"][0])
            }

        self.polygons = polygons


    def locate_point(self, x_coord: float, y_coord: float) -> Tuple[str, str]:
        """ Find the name of the area containing a point, if any. """

        point = Point(x_coord, y_coord)

        for area_name in self.polygons:
            if point.within(self.polygons[area_name]["polygon"]):
                return (area_name, self.polygons[area_name]["id"])

        return (None, None)


def clean_tweet_text(text: str) -> str:
    """ Clean the text of a tweet so that it is ready for classification,
    converting it to lowercase and removing punctuation and non-word
    characters. """

    text = text.lower().split()
    cleaned_text = []

    for word in text:
        if word.isalpha() and not word.startswith("http"):
            cleaned_text.append(word)

    return " ".join(word for word in cleaned_text)


def tag_tweet(tweet: dict, area_boundaries: GeoBoundaries, classifier: flair.models.TextClassifier) -> dict:
    """ Return a modified tweet, with its data cleaned and having been tagged
    with its area and classification, given a passed geoJSON area file and a
    classifier. """

    if "doc" in tweet:
        tweet = tweet["doc"]

    if tweet.get("lang") != "en" or tweet.get("geo") is None:
        # Ignore non-English or non-geo-located tweets
        return

    # Get the basic parameters of the tweet
    tagged_tweet = {}
    tagged_tweet["_id"] = tweet.get("_id")
    tagged_tweet["id"] = tweet.get("_id")
    tagged_tweet["lang"] = tweet.get("lang")
    tagged_tweet["location"] = tweet.get("location")
    tagged_tweet["time"] = tweet.get("time")

    # Find the area in which the tweet was made
    geo = tweet.get("geo")
    tagged_tweet["geo"] = geo

    suburb_tag, suburb_id_tag = area_boundaries.locate_point(
        geo["coordinates"][1],
        geo["coordinates"][0]
    )

    if suburb_tag is None:
        # Ignore tweets not in the area of interest
        return

    tagged_tweet["suburb_tag"] = suburb_tag
    tagged_tweet["suburb_id_tag"] = suburb_id_tag

    # Predict the sentiment of the tweet
    if "full_text" in tweet:
        text = tweet["full_text"]
    elif "text" in tweet:
        text = tweet["text"]
    else:
        return

    cleaned_text = clean_tweet_text(text)
    if cleaned_text == "" or cleaned_text == "rt":
        # Ignore tweets with no words written
        return

    tagged_tweet["tokens"] = cleaned_text

    tokenised_text = flair.data.Sentence(cleaned_text)
    classifier.predict(tokenised_text)

    sentiment = tokenised_text.labels[0]._value
    sentiment_strength = tokenised_text.labels[0]._score

    if sentiment_strength < 0.7:
        # Ignore tweets without any strong sentiment
        return

    tagged_tweet["sentiment"] = sentiment
    tagged_tweet["sentiment_strength"] = sentiment_strength

    return tagged_tweet


def process_tweet_range(extract_db: couchdb.Database, insert_db: couchdb.Database,
    area_boundaries: GeoBoundaries, classifier: flair.models.TextClassifier,
    start_end_range: Tuple[str, str]) -> int:
    """ Given an id range of tweets to be extracted from couchDB, process the
    tweets into the given database, tagging them with the area they were made
    from and their sentiment. """

    start_range = start_end_range[0]
    end_range = start_end_range[1]

    # Download and tag geo-located tweets in the specified id range
    tagged_tweets = []

    tweets = get_tweets_in_range(extract_db, start_range, end_range)
    for tweet in tweets:
        tagged_tweet = tag_tweet(tweet, area_boundaries, classifier)
        if tagged_tweet is not None:
            tagged_tweets.append(tagged_tweet)

    # Load the tagged tweets into couchDB
    output = bulk_put_tweets(insert_db, tagged_tweets)
    return len(output)