"""Feed class definition.

  Feed respresents a web feed such as RSS and ATOM.

  Typical usage example:

  from util.feed import Feed
  from util.feed_db import FeedDB

  feed_db = FeedDB()
  feed = Feed(
      feed_type = "RSS", url = "https://www.example.com/rss",
      title = "Sample Title", changerate = 86400, label = "sample",
      description = "sample description", language = "ko",
      generator = "Sample generator")

  feed_db.insert(feed)
"""
from util.url import url_to_hashkey

class FeedItem:
    """FeedItem to hold an item from a feed.

    Attributes:
      url string: The URL of an item.
      title string: The title of an item.
      description string: The description.
      published_date datetime: The published date of an item.
      author string: The author of an item.
    """
    def __init__(
        self, url, title, description, published_date, author):
        self.url = url
        self.title = title
        self.description = description
        self.published_date = published_date
        self.author = author

class Feed:
    """Feed class representing a web feed.

    Feed instance is used to read or store from/to Feed table.

    Attributes:
      Various fields (see the __init__ function).
    """
    def __init__(
            self, url, title, description, language, url_key = "",
            feed_type = "RSS", changerate = 0, label = "",
            generator = "", popularity = 0, first_fetched_time = 0,
            latest_fetched_time = 0, latest_item_url = "",
            latest_item_title = ""):
        if url_key == "":
            self.url_key = url_to_hashkey(url)
        else:
            self.url_key = url_key
        self.url = url
        self.title = title
        self.description = description
        self.language = language
        self.feed_type = feed_type
        self.changerate = changerate
        self.label = label
        self.generator = generator
        self.popularity = popularity
        self.first_fetched_time = first_fetched_time
        self.latest_fetched_time = latest_fetched_time
        self.latest_item_url = latest_item_url
        self.latest_item_title = latest_item_title

    def __str__(self):
        """Returns a human-readable string.
        """
        return f"""Feed({self.url_key})
  title: {self.title}
  url: {self.url}
  language: {self.language}
  inferred type: {self.feed_type}
  changerate: {self.changerate}
  label: {self.label}
  generator: {self.generator}
  description: {self.description}"""

    def is_valid(self):
        """Check if the data in this instance is valid.

        Returns:
        True if it's valid or False.
        """
        # Check if required fields are filled.
        if self.url == "" or self.url_key == "" or self.title == "":
            return False

        # Check if the hash of the URL matches the hash field.
        if  self.url_key != url_to_hashkey(self.url):
            return False

        return True
