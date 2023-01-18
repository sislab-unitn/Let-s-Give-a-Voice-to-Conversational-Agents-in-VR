#!/bin/sh
for FILE_PATH in 
FILE=$(cat $FILE_PATH)
echo $FILE
curl -XPOST 'https://api.wit.ai/utterances?v=20221114' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$FILE"
# export TOKEN="YOUR_TOKEN"; export FILE_PATH; sh post_utterance.sh