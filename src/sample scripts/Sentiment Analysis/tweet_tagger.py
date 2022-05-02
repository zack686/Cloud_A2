# Libraries for Sentiment Classifier
import json
import re
import flair 
import couchdb 
import sys

# Libaries for Location Tagger
from shapely import geometry
from shapely.geometry  import Point






### Sentiment Classifier ###
clf = flair.models.TextClassifier.load("en-sentiment") # load Classifier

# Twitter Text Preprocessing
def preprocess_text(text):
  text = text.lower().split(" ") # lower case
  text_alpha = []
  for word in text:
    if word.isalpha() == True: # retain only alphabetic
      if re.search(r'http\S+', word) is None: # remove Links
        text_alpha.append(word)
  cleaned = ' '.join(word for word in text_alpha) # converting to sentence
  return cleaned

# Classifying Tweets
def classify(tweet):
    processed = preprocess_text(tweet["text"])
    if processed != "" and processed != "rt" and tweet["coordinates"] != None: #Throwaway Tweets with empty strings or null coordinates
        text_tokenized = flair.data.Sentence(processed)
        clf.predict(text_tokenized) 
        instance = {"id": tweet["_id"], "location": tweet["location"], "coordinates": tweet["coordinates"], "time": tweet["created_at"], "tokens" : processed, "sentiment" : text_tokenized.labels[0]._value}
    else:
        instance = None
    return instance






### Location Tagger ###
suburb_polygons = {}
suburb_ids ={}
lga_polygons = {}
lga_ids = {}

# Load geojsons and save polygon information
with open("vic_states.json") as suburbs:
        suburbs_dat = json.load(suburbs)["features"]

with open("vic_lga.json") as lga:
        lga_dat = json.load(lga)["features"]

for suburb in suburbs_dat:
    temp_poly = geometry.Polygon(suburb["geometry"]["coordinates"][0])
    name = suburb["properties"]["vic_loca_2"]
    suburb_polygons[name] = temp_poly
    suburb_ids[name] = suburb["id"]

for lga in lga_dat:
    temp_poly = geometry.Polygon(lga["geometry"]["coordinates"][0][0])
    name = lga["properties"]["vic_lga__3"]
    lga_polygons[name] = temp_poly
    lga_ids[name] = lga["id"]

# Tag Location
def locate(tweet, suburb_polygons, lga_polygons, suburb_ids, lga_ids):
    loc = tweet["coordinates"]["coordinates"]
    location = Point(loc[0], loc[1])

    for suburb in suburb_polygons:
        if location.within(suburb_polygons[suburb]):
            suburb_tag = suburb
            suburb_id_tag = suburb_ids[suburb]
    for lga in lga_polygons:
        if location.within(lga_polygons[lga]):
            lga_tag = lga
            lga_id_tag = lga_ids[lga]
    return suburb_tag, suburb_id_tag, lga_tag, lga_id_tag






### MAIN FUNCTION ###

def main():
    ### Couchdb connector ###
    couch = couchdb.Server('http://admin:password@172.26.131.127:5984') # need to mask
    raw_db = couch['twitter']
    tagged_db = couch['tagged']

    # Retrieve Unclassified Tweets
    with open('unclassified.txt', 'r') as file:
        Lines = file.readlines()

    # Classify & Tag
    for id in Lines:
        tweet = raw_db[id.rstrip("\n")]
        info = classify(tweet)
        if info == None:
            continue
        suburb_tag, suburb_id_tag, lga_tag, lga_id_tag = locate(tweet, suburb_polygons, lga_polygons, suburb_ids, lga_ids)
        info["suburb_tag"] = suburb_tag
        info["suburb_id_tag"] = suburb_id_tag
        info["lga_tag"] = lga_tag
        info["lga_id_tag"] = lga_id_tag
        tagged_db.save(info)

main()