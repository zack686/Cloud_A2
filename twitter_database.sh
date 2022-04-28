#!/bin/sh
curl -X PUT "http://admin:password@172.26.130.11:5984/twitter"
curl -X POST "http://admin:password@172.26.130.11:5984/twitter/_bulk_docs" \
    -H "Content-Type: application/json" \
    -d @./tinyTwitter.json