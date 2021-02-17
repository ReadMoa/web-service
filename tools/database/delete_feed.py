"""Delete a feed from a Feeds table

Commands:
$ PYTHONPATH=./ python3 tools/database/delete_feed.py \n
  --mode=test --key=deadbeefdeadbeefdeadbeef
"""
import getopt
import sys

from util.feed_db import FeedDB
from util.feed_db import FeedFetchLogDB

def main(argv):
    """main function.
    """
    mode = "test"
    key = ""

    try:
        opts, _ = getopt.getopt(argv,"hm:k:",["mode=","key="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("delete_feed.py -m <mode: prod, dev, test(default)> -k <key>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("delete_feed.py -m <mode: prod, dev, test(default)> -k <key>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)
        elif opt in ("-k", "--key"):
            key = arg

    feed_db = FeedDB(mode=mode)
    fetchlog_db = FeedFetchLogDB(mode=mode)

    feed = feed_db.lookup_feed(url_key=key)
    if not feed:
        print("No feed with [url_key: %s] found." % (key))
        return

    print("""Feed to delete: {key} {url}
    Title: {title}
    First fetched time: {first_fetched_time}""".format(
        key=feed.url_key, url=feed.url,
        title=feed.title, first_fetched_time=feed.first_fetched_time))

    yes_no = input("Delete(Y/n)? ")
    if yes_no == "Y":
        fetchlog_db.delete_by_feed(feed_key=key)
        feed_db.delete_feed(url_key=key)
        print("Feed deleted.")
    else:
        print("Feed not deleted.")

if __name__ == "__main__":
    main(sys.argv[1:])
