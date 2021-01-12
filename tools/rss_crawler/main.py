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

import requests
from util.feed_db import FeedDB
from util.post import post_from_feed_item
from util.post_db import PostDB
from util.feed_reader_factory import FeedReaderFactory, infer_feed_type

# Uncomment to output logging messages.
#import sys
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

MAX_NUM_RECORDS_TO_READ_PER_FEED = 2
AGE_LIMIT_FOR_PAGE = 86400 * 1 # seconds

def read_feed_file(feed_filepath):
    """Parses a feed list file and returns a list of feed URLs.

    Args:
      feed_filepath: A path to the file that contains a list of RSS feeds.

    Returns:
      A list of RSS feed URLs.
    """
    urls = []

    with open(feed_filepath) as feed_file:
        content = feed_file.readlines()

    for line in content:
        line = line.strip()
        if line == '' or line[0] == '#':
            continue
        urls.append(line)

    return urls

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

def process_feed(_, post_db, url):
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

    items = reader.read(count=MAX_NUM_RECORDS_TO_READ_PER_FEED)

    num_new_posts = 0
    for item in items:
        post = post_from_feed_item(item)
        logger.info(
            "Incoming link: Key - %s, URL - %s", post.key, post.post_url)
        age = datetime.now(timezone.utc) - post.published_date
        if age.total_seconds() > AGE_LIMIT_FOR_PAGE:
            logging.info("Too old - %s, %s ago", post.published_date, age)
            continue

        if not post_db.lookup(post.key):
            num_new_posts += 1
            post_db.insert(post)
    return num_new_posts

def main(argv):
    """Main entry point.

    Reads and parses RSS feeds. Insert new entries into the post database.

    Args:
        N/A
    """
    mode = "test"
    feed_file = ""
    try:
        opts, _ = getopt.getopt(argv,"hm:f:",["mode=","file="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("main.py -m <mode: prod, dev, test(default)> -f <file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("main.py -m <mode: prod, dev, test(default)> -f <file>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)
        elif opt in ("-f", "--file"):
            feed_file = arg

    post_db = PostDB(mode)
    feed_db = FeedDB(mode)

    feed_urls = []
    if feed_file:
        feed_urls = read_feed_file(feed_file)
    else:
        feed_urls = [feed.url for feed in feed_db.scan_feeds(
            start_idx=0, count=10000)]

    total_new_posts = 0
    for feed_url in feed_urls:
        print("RSS processing started for ", feed_url)
        num_new_posts = process_feed(feed_db, post_db, feed_url)
        total_new_posts += num_new_posts

        #add_content_to_database(parsed_content)
        print(
            "RSS processing completed for %s (%d new posts)." %
            (feed_url, num_new_posts))

    print("The full RSS import completed (%d new posts)." % (total_new_posts))


if __name__ == "__main__":
    main(sys.argv[1:])
