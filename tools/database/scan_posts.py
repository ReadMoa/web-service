"""Scan Post table

Commands:
$ PYTHONPATH=./ python3 tools/database/scan_posts.py --mode=test --rows=10
"""
import getopt
import sys

from util.post_db import PostDB

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

    post_db = PostDB(mode=mode)

    recent_posts = post_db.scan(count=num_rows)
    for post in recent_posts:
        if output == "verbose":
            print("""Post[{key}] {url}
    Title: {title}
    Author: {author} ({author_hash})
    Main image: {main_image}
    Published date: {published_date}
    Submission time: {submission_time}""".format(
                        key=post.key, url=post.post_url,
                        author=post.author, author_hash=post.author_hash,
                        main_image=post.main_image_url,
                        published_date=post.published_date,
                        title=post.title, submission_time=post.submission_time))
        else:
            print("Post[{key}] {url}".format(key=post.key, url=post.post_url))

    print("Retrieved %d records." % (len(recent_posts)))

if __name__ == "__main__":
    main(sys.argv[1:])
