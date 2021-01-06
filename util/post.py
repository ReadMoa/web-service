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


class Post:
    """Post class to hold a post record.

    A Post instance is an object to hold retrieved information from PostDB or
    to prepare a record for PostDB.

    Attributes:
      Various fields (see the first __init__ function).
    """
    def __init__(
        self, post_url, title, main_image_url = "", description = "",
        user_display_name = "리드모아", user_email = "admin@readmoa.net",
        user_photo_url = "/static/readmoa_profile.png",
        user_provider_id = "ReadMoa", user_id = "ReadMoa",
        submission_time = datetime.utcnow()):
        self.post_url = post_url
        self.post_url_hash = url_to_hashkey(post_url)
        self.key = self.post_url_hash
        self.title = title
        self.main_image_url = main_image_url
        self.description = description
        self.user_display_name = user_display_name
        self.user_email = user_email
        self.user_photo_url = user_photo_url
        self.user_provider_id = user_provider_id
        self.user_id = user_id
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
