"""Update serving storage with PostDB.

Reads posts from PostDB and updates serving storage for new posts.

  Typical usage example:
  $ PYTHONPATH=./ python3 tools/serving/update_serving_data.py -m <mode: prod, dev, test(default)>
"""
import getopt
import logging
import sys

from util.serving_data_manager import ServingDataManager

SERVING_PATH = "serving/"

logger = logging.getLogger()

def main(argv):
    """Main entry point.

    Delete tables and recreate them.

    Args:
        --mode: {prod, dev, test} prod/dev/test mode for a table set.
    """
    mode = "test"

    try:
        opts, _ = getopt.getopt(argv,"hm:",["mode="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("reset_post_tables.py -m <mode: prod, dev, test(default)> -d <dryrun: true(default), false>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("reset_post_tables.py -m <mode: prod, dev, test(default)> -d <dryrun: true(default), false>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)

    print("Storage update started.")

    serving_data_manager = ServingDataManager(mode=mode, serving_path=SERVING_PATH)
    serving_data_manager.update_storage()

    print("Storage update completed.")

if __name__ == "__main__":
    main(sys.argv[1:])
