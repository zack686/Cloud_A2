#!/bin/bash
curl -X PUT "http://admin:password@172.26.134.4:5984/twitter/_design/untagged_tweets" -d "@./designDocuments/untagged_tweets.json"
curl -X GET "http://admin:password@172.26.134.4:5984/twitter/_design/untagged_tweets/_view/untagged_geo_tweets?reduce=true&group=true"