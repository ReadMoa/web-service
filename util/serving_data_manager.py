"""ServingDataManager class definition.

  ServingDataManager updates/cleans up data in the serving directory.

  Typical usage example:

  from serving_data_manager import ServingDataManager

  serving_data_manager = ServingDataManager(mode="dev")
  serving_data_manager.update_storage()

  serving_data_manager.garbage_collect()
"""
import glob
import logging
from os import listdir, mkdir
from os.path import isdir, isfile, join

import jsonpickle
from util.post_db import PostDB

NUM_POSTS_TO_STORE = 1000
PATH_FOR_LATEST_POSTS = "latest"
FILENAME_DONE = "done"

logger = logging.getLogger()

def remove_line_break(src_str):
    """Replaces link breaks (NL, CR) into whitespaces.

    Args:
        src_str string: A source string.

    Returns:
        A modified string.
    """
    dst_str = src_str
    return dst_str.replace('\n', ' ').replace('\r', '')

class ServingDataManager:
    """ServingDataManager manages serving data.

    Directories:
      {serving_path}/latest: Stores the latest posts.

    Filename format:
      {hash_url}-{submission timestamp}.json

    Attributes:
      Various fields (see the first __init__ function).
    """
    def __init__(self, mode, serving_path):
        """Initializes ServingDataManager.

        Will create /latest directory under serving_path.

        Args:
          mode string: test/dev/prod
          serving_path: A root directory for storing serving posts.
        """
        self.mode = mode
        # Create the serving directory if not exist.
        path = join(serving_path, PATH_FOR_LATEST_POSTS)
        if not isdir(path):
            mkdir(path)
            logger.info("Serving path created: %s", path)
        self.serving_path = serving_path

    def update_storage(self):
        """Updates serving storage with latest posts from PostDB.
        """
        post_db = PostDB(mode=self.mode)

        # Read files in the serving directory.
        path = join(self.serving_path, PATH_FOR_LATEST_POSTS)
        done_path = join(path, FILENAME_DONE)
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

        # Filename: {hash_key}-{submission timestamp}.json
        recent_posts = post_db.scan(count=NUM_POSTS_TO_STORE)

        # Read the previous timestamp that is stored in done file.
        latest_ts = 0
        seen_newer_submission = False
        if isfile(done_path):
            with open(done_path, "r") as infile:
                latest_ts = int(infile.read())

        for post in recent_posts:
            submission_ts = int(post.submission_time.timestamp())
            new_filename = "{hash_key}-{ts}.json".format(
                hash_key=post.post_url_hash,
                ts=str(submission_ts))

            if submission_ts > latest_ts:
                latest_ts = submission_ts
                seen_newer_submission = True

            # Create a new file if they are not there.
            if new_filename not in onlyfiles:
                logger.info("New post to write: %s", new_filename)

                with open(join(path, new_filename), "w") as outfile:
                    post_json = jsonpickle.encode(post)
                    #json_str = json.dumps(post_json, indent=4)
                    outfile.write(post_json)

        if seen_newer_submission:
            with open(done_path, "w") as outfile:
                outfile.write(str(latest_ts))


    def read_posts_from_storage(self):
        """Reads posts from serving storage (/latest).

        Returns:
          A list of Post instances from the serving storage.
        """
        path = join(self.serving_path, PATH_FOR_LATEST_POSTS)
        files = glob.glob(path + "/*.json")

        posts = []
        for filename in files:
            with open(filename, "r") as infile:
                post = jsonpickle.decode(infile.read())
                posts.append(post)
        return posts

    def garbage_collect(self):
        """Garbage collects old posts in the serving storage
        """
