"""Tool to update author hash (one-off tool).

Commands:
$ PYTHONPATH=./ python3 tools/database/update_author_hash.py --mode=test --nodryrun
"""
import getopt
import sys

from util.post_db import PostDB
from util.url import author_to_hashkey

def main(argv):
    """main function.
    """
    mode = "test"
    num_rows = 1000
    dryrun = True

    try:
        opts, _ = getopt.getopt(argv,"hm:n:",["mode=","nodryrun"])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("update_author_hash.py -m <mode: prod, dev, test(default)> "
              "-n <nodryrun>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("update_author_hash.py -m <mode: prod, dev, test(default)> "
                  "-n <nodryrun>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)
        elif opt in ("-n", "--nodryrun"):
            dryrun = False

    post_db = PostDB(mode=mode)

    start_idx = 0
    total_records = 0
    while True:
        recent_posts = post_db.scan(start_idx=start_idx, count=num_rows)
        for post in recent_posts:
            new_author_hash = author_to_hashkey(post.author)

            print("---------------------------------------------------------")
            print("""Post[{key}] {url}
    Author: {author} (old hash: {old_hash}, new hash: {new_hash})""".format(
            key=post.key, url=post.post_url,
            author=post.author, old_hash=post.author_hash,
            new_hash=new_author_hash))

            if dryrun:
                continue

            post_db.delete(key=post.key)
            print("DELETED")
            post_db.insert(post=post)
            print("INSERTED AGAIN")
            print("---------------------------------------------------------")

        total_records += len(recent_posts)
        if len(recent_posts) < num_rows:
            break

    print("Retrieved %d records." % (total_records))

if __name__ == "__main__":
    main(sys.argv[1:])
