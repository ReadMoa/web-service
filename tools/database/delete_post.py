"""Delete a post from a Post table

Commands:
$ PYTHONPATH=./ python3 tools/database_management/delete_post.py \n
  --mode=test --key=deadbeefdeadbeefdeadbeef
"""
import getopt
import sys

from util.post_db import PostDB

def main(argv):
    """main function.
    """
    mode = "test"
    key = ""

    try:
        opts, _ = getopt.getopt(argv,"hm:k:",["mode=","key="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("scan_posts.py -m <mode: prod, dev, test(default)> -k <key>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("scan_posts.py -m <mode: prod, dev, test(default)> -k <key>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)
        elif opt in ("-k", "--key"):
            key = arg

    post_db = PostDB(mode=mode)

    post = post_db.lookup(key=key)
    print("""Post to delete: {key} {url}
    Title: {title}
    Submission time: {submission_time}""".format(
        key=post.key, url=post.post_url,
        title=post.title, submission_time=post.submission_time))

    yes_no = input("Delete(Y/n)? ")
    if yes_no == "Y":
        post_db.delete(key=key)
        print("Post deleted.")
    else:
        print("Post not deleted.")

if __name__ == "__main__":
    main(sys.argv[1:])
