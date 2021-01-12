"""Scan Feeds table

Commands:
$ PYTHONPATH=./ python3 tools/database_management/scan_feeds.py --mode=test --rows=10
"""
import getopt
import sys

from util.feed_db import FeedDB

def main(argv):
    """main function.
    """
    mode = "test"
    num_rows = 10
    output = "concise"

    try:
        opts, _ = getopt.getopt(argv,"hm:r:o:",["mode=","rows=","output="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("scan_posts.py -m <mode: prod, dev, test(default)> -r <rows>"
              " -o <output: concise, verbose>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("scan_posts.py -m <mode: prod, dev, test(default)> -r <rows>"
                  " -o <output: concise, verbose>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)
        elif opt in ("-r", "--rows"):
            num_rows = int(arg)
        elif opt in ("-o", "--output"):
            if arg in ("concise", "verbose"):
                output = arg
            else:
                print("Unknown 'output': %s", arg)
                sys.exit(2)

    feed_db = FeedDB(mode=mode)

    recent_feeds = feed_db.scan_feeds(count=num_rows)
    for feed in recent_feeds:
        if output == "verbose":
            print("""Feed[{key}] {url}
    Title: {title}
    Feed type: {feed_type}, Generator: {generator}
    Language: {language}, Changerate: {changerate}, Popularity: {popularity}
    Label: {label}
    First fetched time: {first_fetched_time}
    Latest fetched time: {latest_fetched_time}
    Latest item URL: {latest_item_url}
    Latest item title: {latest_item_title}
    """.format(
                key=feed.url_key, url=feed.url, title=feed.title,
                feed_type=feed.feed_type, generator=feed.generator,
                language=feed.language, changerate=feed.changerate,
                popularity=feed.popularity, label=feed.label,
                first_fetched_time=feed.first_fetched_time,
                latest_fetched_time=feed.latest_fetched_time,
                latest_item_url=feed.latest_item_url,
                latest_item_title=feed.latest_item_title))
        else:
            print("Post[{url_key}] {url}".format(url_key=feed.url_key, url=feed.url))

    print("Retrieved %d records." % (len(recent_feeds)))

if __name__ == "__main__":
    main(sys.argv[1:])
