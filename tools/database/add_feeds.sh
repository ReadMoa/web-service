#!/bin/bash
#
# $ ./tools/database/add_feeds.sh test ./tools/rss_crawler/feeds.txt

echo "----------------------------------------------"
echo "START updating serving storage"
echo "----------------------------------------------"

START=$(date +%s)

mode=$1
filename=$2
while read line; do
    [[ "$line" =~ ^#.*$ ]] && continue
    [ -z "$line" ] && continue
    # reading each line
    echo Insert into Feeds table: $line
    PYTHONPATH=./ python3 tools/database/add_a_feed.py --mode=$mode --url=$line
done < $filename

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)

echo "----------------------------------------------"
echo "COMPLETED updating serving storage (time passed: $DIFF seconds)"
echo "----------------------------------------------"
