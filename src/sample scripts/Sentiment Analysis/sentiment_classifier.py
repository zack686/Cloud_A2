# Importing required libaries
import json
import re
import flair # Needs to be pip installed
import couchdb 
import sys
clf = flair.models.TextClassifier.load("en-sentiment") # Load Classifier

# Clean text for model input
def preprocess_text(text):
  text = text.lower().split(" ") # lower case
  text_alpha = []
  for word in text:
    if word.isalpha() == True: #retain only alphabetic
      if re.search(r'http\S+', word) is None: # Remove Links
        text_alpha.append(word)
  cleaned = ' '.join(word for word in text_alpha) # converting to sentence
  return cleaned

# Couchdb connector
couch = couchdb.Server('http://admin:password@172.26.131.127:5984')
raw_twitter_db = couch['twitter']
clf_coord = couch['clf_coordinate']
clf_null = couch['clf_null']

# Retrieve Unclassified text
with open('unclassified.txt', 'r') as file:
  Lines = file.readlines()

if len(Lines) == 0: # Close script if no new IDs
  sys.exit()

# Creating dataset
for id in Lines:
    #doc = raw_twitter_db[tweet]
    #tweet = doc["doc"]
    tweet = raw_twitter_db[id.rstrip("\n")]
    processed = preprocess_text(tweet["text"])

    if processed != "" and processed != "rt": #Throwaway Tweets with empty strings
      text_tokenized = flair.data.Sentence(processed)
      clf.predict(text_tokenized) 
      instance = {"id": tweet["_id"], "location": tweet["location"], "coordinates": tweet["coordinates"], 
      "time": tweet["created_at"], "tokens" : processed, "sentiment" : text_tokenized.labels[0]._value}
      if instance["coordinates"] != None:
        clf_coord.save(instance)
      else:
        clf_null.save(instance)

file.truncate(0)
file.close()