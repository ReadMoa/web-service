"""Add a feed to Feeds table.

Commands:
$ PYTHONPATH=./ python3 tools/rss_crawler/add_a_feed.py \
        --mode=test --feed_type=rss --url=https://example.com/rss
"""
from datetime import datetime
import getopt
import logging
import sys

import requests
from util.feed import Feed
from util.feed_db import FeedDB
from util.feed_reader_factory import FeedReaderFactory, infer_feed_type
from util.url import url_to_hashkey

logger = logging.getLogger()

def main(argv):
    """main function.
    """
    mode = "test"
    url = ""
    feed_type = ""

    try:
        opts, _ = getopt.getopt(argv,"hm:f:u:",["mode=","feed_type=","url="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("add_a_feed.py -m <mode: prod, dev, test(default)> -f <feed_type>"
              " -u <url>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("add_a_feed.py -m <mode: prod, dev, test(default)> "
                  "-f <feed_type> -u <url>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)
        elif opt in ("-f", "--feed_type"):
            if arg in ("rss", "atom"):
                feed_type = arg.upper()
            else:
                print("Unknown 'feed_type': %s", arg)
                sys.exit(2)
        elif opt in ("-u", "--url"):
            url = arg

    feed_db = FeedDB(mode=mode)

    url_key = url_to_hashkey(url)
    if feed_db.lookup_feed(url_key=url_key):
        print("Feed already exists in {mode}_feeds table: {url}".format(
            mode=mode, url=url))
        sys.exit()

    # Fetch a feed and extract information.
    feed_doc = requests.get(url)

    if feed_doc.status_code != 200:
        logger.warning(
                "Failed to fetch with Response Code %d for %s",
                feed_doc.status_code, feed_doc.url)
        sys.exit(2)

    if not feed_type:
        feed_type = infer_feed_type(url, feed_doc.content)
    reader = FeedReaderFactory().get_reader(
            feed_type=feed_type, url=url, feed_content=feed_doc.content)

    feed = Feed(url=url, title=reader.title,
            description=reader.description,
            language=reader.language, feed_type=feed_type,
            first_fetched_time=datetime.utcnow(),
            latest_fetched_time=datetime.utcnow())

    feed_db.insert_feed(feed)

    feed = feed_db.lookup_feed(url_key=url_key)
    if feed:
        print("""
Feed successfully added: 
  url_key: {url_key}
  URL: {url}
  feed_type: {feed_type}
  title: {title}
  language: {language}
  first fetched time: {first_fetched_time}
  latest fetched time: {latest_fetched_time}
  description: {description}""".format(
          url_key=feed.url_key, url=feed.url,
          feed_type=feed.feed_type, title=feed.title,
          language=feed.language, first_fetched_time=feed.first_fetched_time,
          latest_fetched_time=feed.latest_fetched_time,
          description=feed.description))
    else:
        print("Feed failed to add: %s" % (url))

if __name__ == "__main__":
    main(sys.argv[1:])
