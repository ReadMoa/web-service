"""RSS Crawling tool.

Fetches RSS feeds listed in feeds.txt and insert new entries from the feeds
to the post table.

  Typical usage example:
  $ PYTHONPATH=./ python3 tools/rss_crawler/main.py
"""
from datetime import datetime, timezone
import getopt
import logging
import sys

import pytz
import requests
from util.feed_db import FeedDB, FeedFetchLogDB
from util.post import post_from_feed_item
from util.post_db import PostDB
from util.feed_reader_factory import FeedReaderFactory, infer_feed_type
from util.url import url_to_hashkey

# Uncomment to output logging messages.
#import sys
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

MAX_NUM_RECORDS_TO_READ_PER_FEED = 2
AGE_LIMIT_FOR_PAGE = 86400 * 1 # seconds

def fetch_rss(url):
    """Fetch RSS document from the given URL.

    Args:
      url: URL for RSS XML document.

    Returns:
      The content of RSS document.
    """
    rss_doc = requests.get(url)

    if rss_doc.status_code != 200:
        logger.warning(
                "Failed to fetch with Response Code %d for %s",
                rss_doc.status_code, rss_doc.url)

    return rss_doc.content

def process_feed(feed_db, post_db, log_db, url):
    """Process one feed.

    Fetches a web feed, insert new posts into posts table.

    Args:
      feed_db: Feeds database instance.
      post_db: Posts database instance.
      url: URL for RSS XML document.

    Returns:
      The # of new posts inserted into posts table.
    """
    feed_content = fetch_rss(url)

    feed_type = infer_feed_type(url, feed_content)
    reader = FeedReaderFactory().get_reader(
        feed_type=feed_type, url=url, feed_content=feed_content)
    fetched_time = datetime.utcnow()

    items = reader.read(count=MAX_NUM_RECORDS_TO_READ_PER_FEED)

    num_new_posts = 0
    newest_post_published_date = datetime(1970, 1, 1, tzinfo=pytz.UTC)
    for item in items:
        post = post_from_feed_item(item)
        logger.info(
            "Incoming link: Key - %s (published: %s), URL - %s", post.key,
            post.published_date, post.post_url)
        age = datetime.now(timezone.utc) - post.published_date
        if age.total_seconds() > AGE_LIMIT_FOR_PAGE:
            logging.info("Too old - %s, %s ago", post.published_date, age)
            continue

        if not post_db.lookup(post.key):
            num_new_posts += 1
            post_db.insert(post)

        # Keeps the newest published time.
        if post.published_date > newest_post_published_date:
            newest_post_published_date = post.published_date

    # Log a feed fetch event.
    url_key = url_to_hashkey(url)
    feed_updated = (num_new_posts > 0)

    feed = feed_db.lookup_feed(url_key)
    log_db.log(
        url_key, fetched_time, feed_updated, newest_post_published_date,
        feed.changerate, feed.scheduled_fetch_time)
    feed_db.update_changerate(url_key)
    return num_new_posts

def main(argv):
    """Main entry point.

    Reads and parses RSS feeds. Insert new entries into the post database.

    Args:
        N/A
    """
    mode = "test"
    try:
        opts, _ = getopt.getopt(argv,"hm:",["mode="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("main.py -m <mode: prod, dev, test(default)>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("main.py -m <mode: prod, dev, test(default)>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)

    post_db = PostDB(mode)
    feed_db = FeedDB(mode)
    log_db = FeedFetchLogDB(mode)

    feeds = feed_db.scan_feeds(start_idx=0, count=10000)

    total_new_posts = 0
    rss_import_start_time = datetime.utcnow()
    print("[RSS import] began at %s" % (rss_import_start_time))
    for feed in feeds:
        if datetime.utcnow() > feed.scheduled_fetch_time:
            print("RSS processing started for ", feed.url)
            num_new_posts = process_feed(feed_db, post_db, log_db, feed.url)
            total_new_posts += num_new_posts
            print(
                "RSS processing completed for %s (%d new posts)." %
                (feed.url, num_new_posts))
        else:
            print(
                "RSS processing skipped (scheduled at %s): %s" %
                (feed.scheduled_fetch_time, feed.url))

    rss_import_end_time = datetime.utcnow()
    print("[RSS import] completed (%d new posts) at %s (duration: %s)" % (
        total_new_posts, rss_import_end_time,
        rss_import_end_time - rss_import_start_time))

if __name__ == "__main__":
    main(sys.argv[1:])
