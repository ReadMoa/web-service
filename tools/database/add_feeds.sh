#!/bin/bash
#
# $ ./tools/rss_crawler/add_feeds.sh test ./tools/rss_crawler/feeds.txt

echo ----------------------------------------------
echo START adding feeds
echo ----------------------------------------------

mode=$1
filename=$2
while read line; do
    [[ "$line" =~ ^#.*$ ]] && continue
    [ -z "$line" ] && continue
    # reading each line
    echo Insert to Feeds table: $line
    cat tools/rss_crawler/add_a_feed.py
    PYTHONPATH=./ python3 tools/database/add_a_feed.py --mode=$mode --url=$line
done < $filename

echo ----------------------------------------------
echo COMPLETED adding feeds
echo ----------------------------------------------