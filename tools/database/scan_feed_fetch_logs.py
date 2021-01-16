"""Scan Feeds table

Commands:
$ PYTHONPATH=./ python3 tools/database/scan_feed_fetch_logs.py \
    --mode=test --rows=10 --feed_url=https://example.com/rss.xml
"""
import getopt
import sys

from util.feed_db import FeedFetchLogDB
from util.url import url_to_hashkey

def main(argv):
    """main function.
    """
    mode = "test"
    num_rows = 10
    feed_url = ""

    try:
        opts, _ = getopt.getopt(argv,"hm:r:f:",["mode=","rows=","feed_url="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("scan_feed_fetch_logs.py -m <mode: prod, dev, test(default)>"
              " -r <rows> -f <feed_url>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("scan_feed_fetch_logs.py -m <mode: prod, dev, test(default)>"
                  " -r <rows> -f <feed_url>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)
        elif opt in ("-r", "--rows"):
            num_rows = int(arg)
        elif opt in ("-f", "--feed_url"):
            feed_url = arg

    feed_fetch_log_db = FeedFetchLogDB(mode=mode)
    url_key = url_to_hashkey(feed_url)

    recent_events = feed_fetch_log_db.scan(url_key=url_key, count=num_rows)
    for event in recent_events:
        print("""Event[{key}] {url}
    Fetched time: {fetched_time}
    Feed updated: {feed_updated}
    newest_post_published_date: {newest_post_published_date}
    previous_changerate: {previous_changerate}
    previous_scheduled_fetch_time: {previous_scheduled_fetch_time}
    """.format(
        key=url_key, url=feed_url, fetched_time=event["fetched_time"],
        feed_updated=event["feed_updated"],
        newest_post_published_date=event["newest_post_published_date"],
        previous_changerate=event["previous_changerate"],
        previous_scheduled_fetch_time=event["previous_scheduled_fetch_time"]))

    print("Retrieved %d records." % (len(recent_events)))

if __name__ == "__main__":
    main(sys.argv[1:])
