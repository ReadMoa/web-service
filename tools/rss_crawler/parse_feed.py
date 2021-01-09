"""Parses a feed and outputs items.

  Typical usage example:
  $ PYTHONPATH=./ python3 tools/rss_crawler/parse_feed.py \
      --type=rss --num_items=10 --url 'https://brunch.co.kr/rss/@@T8j'
"""
import getopt
import logging
import sys

import requests
from util.feed_reader_factory import FeedReaderFactory

logger = logging.getLogger()

def main(argv):
    """main function.
    """
    url = ""
    num_items = 10
    feed_type = ""

    try:
        opts, _ = getopt.getopt(argv,"hu:n:t:",["url=","num_items=","type="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("parse_feed.py -u <url> -n <num_items> -t <type: rss, atom>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("parse_feed.py -u <url> -n <num_items> -t <type: rss, atom>")
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
        elif opt in ("-n", "--num_items"):
            num_items = int(arg)
        elif opt in ("-t", "--type"):
            feed_type = arg.upper()
            if not feed_type in ("RSS", "ATOM"):
                print("Unknown 'feed_type': %s" % feed_type)
                sys.exit(2)

    feed = requests.get(url)

    if feed.status_code != 200:
        logger.warning(
                "Failed to fetch with Response Code %d for %s",
                feed.status_code, feed.url)

    reader = FeedReaderFactory().get_reader(feed_type=feed_type, url=url, feed_content=feed.content)

    items = reader.read(count=num_items)
    for item in items:
        print("""[{url}]
    Title: {title}
    Author: {author}
    Published date: {published_date}
    Description: {description}
    """.format(
        url=item.url, title=item.title, author=item.author,
        published_date=item.published_date, description=item.description))

    print("Retrieved %d records." % (len(items)))

if __name__ == "__main__":
    main(sys.argv[1:])
