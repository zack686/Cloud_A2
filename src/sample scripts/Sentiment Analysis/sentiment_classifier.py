# Importing required libaries
import json
import re
import flair # Needs to be pip installed

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

# Loading data
f = open('sample.json')
tweets = json.load(f)
tweets = tweets["rows"]

# Creating dataset
texts = []
tweet_info = {}
for row in range(len(tweets)):
  processed = preprocess_text(tweets[row]["doc"]["text"])
  if processed != "": #Throwaway Tweets with empty strings
    texts.append(processed)
    instance = {"location": tweets[row]["doc"]["location"], "coordinates": tweets[row]["doc"]["coordinates"],
    "time": tweets[row]["doc"]["created_at"], "text": tweets[row]["doc"]["text"]}
    tweet_info[tweets[row]["id"]] = instance

# Classifying Tweets
labels = []
clf = flair.models.TextClassifier.load("en-sentiment")
for tweet in texts:
  text_tokenized = flair.data.Sentence(tweet)
  clf.predict(text_tokenized) 
  labels.append(text_tokenized.labels[0]._value)

# Creating labelled output
pos = 0
for id, value in tweet_info.items():
  value["label"] = labels[pos]
  tweet_info[id] = value
  pos += 1

with open('sample_output.json', 'w') as f:
    json.dump(tweet_info, f)
