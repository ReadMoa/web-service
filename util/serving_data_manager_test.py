"""Tests for ServingDataManager class.

Requires: at least one post in PostDB at "test" mode.

Commands:
$ PYTHONPATH=./ python3 util/serving_data_manager_test.py
"""
import os
import glob

from util.serving_data_manager import ServingDataManager

TEST_PATH = "test/"

def clean_storage_space():
    """Cleans up storage space before/after testing.
    """
    print("TEST Clean the test directory.")
    files = glob.glob(TEST_PATH + "latest/*.json")
    for file in files:
        try:
            os.remove(file)
        except OSError as ex:
            print("Error: %s : %s" % (file, ex.strerror))

    files = glob.glob(TEST_PATH + "latest/done")
    for file in files:
        try:
            os.remove(file)
        except OSError as ex:
            print("Error: %s : %s" % (file, ex.strerror))

def test_update_storage():
    """Tests update_storage method.
    """
    serving_data_manager = ServingDataManager(mode="test", serving_path= TEST_PATH)
    serving_data_manager.update_storage()

    clean_storage_space()

def test_read_storage():
    """Tests read_posts_from_storage method.
    """
    # Create post json files.
    serving_data_manager = ServingDataManager(mode="test", serving_path= TEST_PATH)
    serving_data_manager.update_storage()

    posts = serving_data_manager.read_posts_from_storage()
    for post in posts:
        print("[{}] {}".format(post.post_url_hash, post.post_url))
    clean_storage_space()

def main():
    """Run tests for ServingDataManager.
    """
    print("TEST started.")
    clean_storage_space()

    test_update_storage()
    test_read_storage()
    print("TEST completed.")


if __name__ == "__main__":
    main()
