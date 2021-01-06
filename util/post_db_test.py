"""Tests for PostDB class.

Commands:
$ PYTHONPATH=./ python3 tools/database_management/reset_database.py --mode=test --dryrun=false
$ PYTHONPATH=./ python3 util/post_db_test.py
"""
from util.post import Post
from util.post_db import PostDB

# TODO: Find a way to create a local DB instead of the main DB in the cloud.
# TODO: Reset the test tables before every test case.

def test_insert():
    """Test insert operation.
    """
    post_db = PostDB(mode="test")
    post = Post(
        post_url = "https://www.example.com/",
        title = "Test",
        main_image_url = "https://www.example.com/foo.png",
        description = "Bar")

    print(post)
    post_db.insert(post)

    stored_post = post_db.lookup(post.key)

    assert stored_post.title == post.title
    assert stored_post.post_url == post.post_url
    assert stored_post.post_url_hash == post.post_url_hash

    post_db.delete(post.key)

def test_scan():
    """Test scan operation.
    """
    post_db = PostDB(mode="test")
    post1 = Post(
        post_url = "https://www.example.com/1",
        title = "Test1",
        main_image_url = "https://www.example.com/foo1.png",
        description = "Bar1")
    post2 = Post(
        post_url = "https://www.example.com/2",
        title = "Test2",
        main_image_url = "https://www.example.com/foo2.png",
        description = "Bar2")
    post_db.insert(post1)
    post_db.insert(post2)

    recent_posts = post_db.scan()

    assert len(recent_posts) == 2
    assert recent_posts[0].post_url == post1.post_url
    assert recent_posts[1].post_url == post2.post_url

    post_db.delete(post1.key)
    post_db.delete(post2.key)

def main():
    """Run tests for PostDB.
    """
    print("TEST started.")
    test_insert()
    test_scan()
    print("TEST completed.")


if __name__ == "__main__":
    main()
