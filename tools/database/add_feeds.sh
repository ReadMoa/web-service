#!/bin/bash
#
# $ ./tools/rss_crawler/add_feeds.sh test ./tools/rss_crawler/feeds.txt

echo '----------------------------------------------'
echo 'START adding feeds'
echo '----------------------------------------------'

START=$(date +%s.%N)

mode=$1
filename=$2
while read line; do
    [[ "$line" =~ ^#.*$ ]] && continue
    [ -z "$line" ] && continue
    # reading each line
    echo Insert into Feeds table: $line
    PYTHONPATH=./ python3 tools/database/add_a_feed.py --mode=$mode --url=$line
done < $filename

END=$(date +%s.%N)
DIFF=$(echo "$END - $START" | bc)

echo '----------------------------------------------'
echo 'COMPLETED adding feeds (time passed: $DIFF)'
echo '----------------------------------------------'