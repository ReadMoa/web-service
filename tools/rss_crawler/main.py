"""RSS Crawling tool.

Fetches RSS feeds listed in feeds.txt and insert new entries from the feeds
to the post table.

  Typical usage example:
  $ PYTHONPATH=./ python3 tools/rss_crawler/main.py
"""
from datetime import datetime, timezone
import logging
import os
import time

from dateutil.parser import parse
from bs4 import BeautifulSoup
import requests
from util import url as url_util
from util.post import post_from_feed_item
from util.post_db import PostDB
from util.feed_reader_factory import FeedReaderFactory, infer_feed_type

# Uncomment to output logging messages.
#import sys
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

RSS_FEED_FILE = "feeds.txt"
DATABASE_MODE = "prod"
MAX_NUM_RECORDS_TO_READ_PER_FEED = 3
AGE_LIMIT_FOR_PAGE = 86400 * 3 # seconds

post_db = PostDB(DATABASE_MODE)

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

def main():
    """Main entry point.

    Reads and parses RSS feeds. Insert new entries into the post database.

    Args:
        N/A
    """
    feed_path = os.path.join(os.path.dirname(__file__), RSS_FEED_FILE)
    for feed_url in read_feed_file(feed_path):
        print("RSS processing started for ", feed_url)
        feed_content = fetch_rss(feed_url)

        feed_type = infer_feed_type(feed_url, feed_content)
        reader = FeedReaderFactory().get_reader(
            feed_type=feed_type, url=feed_url, feed_content=feed_content)

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

        #add_content_to_database(parsed_content)
        print(
            "RSS processing completed for %s (%d new posts)." %
            (feed_url, num_new_posts))
    print("The full RSS import completed.")


if __name__ == "__main__":
    main()
