"""Post class definition.

  Typical usage example:

  from post import Post
  from post_db import PostDB

  post_db = PostDB()
  post = Post(
      post_url = "https://www.example.com/",
      title = "Test",
      main_image_url = "https://www.example.com/foo.png",
      description = "Bar")
  post_db.insert(post)
"""
from datetime import datetime

from util.url import url_to_hashkey
from util.page_metadata import fetch_main_image_from_post

class Post:
    """Post class to hold a post record.

    A Post instance is an object to hold retrieved information from PostDB or
    to prepare a record for PostDB.

    Attributes:
      Various fields (see the first __init__ function).
    """
    def __init__(
        self, post_url, title, author, published_date, main_image_url = "",
        description = "", user_display_name = "리드모아",
        user_email = "admin@readmoa.net",
        user_photo_url = "/static/readmoa_profile.png",
        user_provider_id = "ReadMoa", user_id = "ReadMoa",
        submission_time = None):
        self.post_url = post_url
        self.post_url_hash = url_to_hashkey(post_url)
        self.key = self.post_url_hash
        self.title = title
        self.author = author
        self.published_date = published_date
        self.main_image_url = main_image_url
        self.description = description
        self.user_display_name = user_display_name
        self.user_email = user_email
        self.user_photo_url = user_photo_url
        self.user_provider_id = user_provider_id
        self.user_id = user_id
        if submission_time is None:
            self.submission_time = datetime.utcnow()
        else:
            self.submission_time = submission_time

    def __str__(self):
        """Returns a human-readable string.
        """
        return f"""POST({self.key})
        title: {self.title}
        url: {self.post_url}
        main_image_url: {self.main_image_url}
        description: {self.description}
        """

    def is_valid(self):
        """Check if the data in this instance is valid.

        Returns:
        True if it's valid or False.
        """
        # Check if required fields are filled.
        if self.post_url == "" or self.post_url_hash == "" or self.title == "":
            return False

        # Check if the hash of the URL matches the hash field.
        if  self.post_url_hash != url_to_hashkey(self.post_url):
            return False

        return True

def post_from_feed_item(feed_item):
    """Creates a Post from a FeedItem data.

    Args:
        feed_item (util.feed_reader_factory.FeedItem): a FeedItem data.
    """
    # Fetches the main image link from the post because FeedItem data
    # doesn't have main image link.
    # NOTE: fetch_main_image_from_post has artificial delays for
    # external connection.
    main_image_url = fetch_main_image_from_post(feed_item.url)

    return Post(
        post_url=feed_item.url, title=feed_item.title,
        author=feed_item.author, published_date=feed_item.published_date,
        description=feed_item.description,
        main_image_url=main_image_url)
