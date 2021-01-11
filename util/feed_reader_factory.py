"""FeedReaderFactory and feed readers

  FeedReaderFactory creates a feed reader by a feed type.

  Typical usage example:

  from util.feed_reader_factory import FeedReaderFactory

  reader = FeedReaderFactory().get_reader(
      feed_type=feed_type, url=url, feed_content=feed.content)
  items = reader.read(count=10)
"""
import logging
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from dateutil.parser import parse


logger = logging.getLogger()

MAX_NUM_RECORDS_TO_READ_PER_FEED = 10000
MAX_SUMMARY_LENGTH = 150

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


def extract_from_post(html):
    """Extracts summary text from a RSS summary record.

    Truncates if the text exceeds the threshold.

    Args:
      html: A text in html.

    Returns:
      An extracted string from the RSS summary record.
    """
    summary_soup = BeautifulSoup(html, "html.parser")
    summary = ""
    if summary_soup.body:
        summary_soup = summary_soup.body

    for text in summary_soup.find_all(text=True):
        summary += "{} ".format(text)
        if len(summary) > MAX_SUMMARY_LENGTH:
            break

    logger.info("Extracted summary: %s", summary[:MAX_SUMMARY_LENGTH])
    return summary[:MAX_SUMMARY_LENGTH]

# <rss version="2.0">
#   <channel>
class RssReader:
    """RssReader parses an RSS feed.

    Attributes:
      feed_content: The content of the feed.
    """
    def __init__(self, feed_content):
        self.feed_content = feed_content
        self.feed_soup = BeautifulSoup(self.feed_content, "xml")

        channel = self.feed_soup.rss.channel
        self.author = ""
        self.title = channel.title.text
        self.description = channel.description.text
        self.language = channel.language.text
        self.generator = channel.generator.text

    def read(self, count=1):
        """Parses the RSS feed and returns 'count' number of items.

        Args:
          count: the number of items to return.

        Returns:
          A list of items parsed from the feed.
        """
        items = []
        num_entries = 0
        for i in self.feed_soup.findAll("item"):
            if num_entries >= count:
                break

            url = i.link.text
            if not url:
                raise ValueError("Empty <link>")

            updated = ""
            if i.find("pubDate"):
                updated = parse(i.find("pubDate").get_text())

            author = ""
            if i.find("author"):
                author = i.find("author").get_text()

            title = i.title.text
            description = extract_from_post(i.description.text)

            items.append(FeedItem(
                url=url, title=title, description=description,
                published_date=updated, author=author))

            num_entries += 1

        return items


class AtomReader:
    """AtomReader parses an ATOM feed.

    Attributes:
      feed_content: The content of the feed.
    """
    def __init__(self, feed_content):
        self.feed_content = feed_content
        self.feed_soup = BeautifulSoup(self.feed_content, "xml")

        feed = self.feed_soup.feed
        self.author = feed.author.name.text
        self.title = feed.title.text
        self.language = ""
        self.description = ""
        self.generator = ""


    def read(self, count=1):
        """Parses the ATOM feed and returns 'count' number of items.

        Args:
          count: the number of items to return.

        Returns:
          A list of items parsed from the feed.
        """
        items = []
        num_entries = 0
        for i in self.feed_soup.find_all("entry"):
            if num_entries >= count:
                break

            url = i.find("link")["href"]

            updated = ''
            if i.find("updated"):
                updated = parse(i.find("updated").get_text())
            author = i.find("author").find("name").get_text()
            description = extract_from_post(i.find("summary").get_text())
            title = i.find("title").get_text()

            items.append(FeedItem(
                url=url, title=title, description=description,
                published_date=updated, author=author))
            num_entries += 1

        return items

def infer_feed_type(url, content):
    """Infer feed type from URL and its content

    Args:
      url (string): A feed URL.
      content (string)

    Returns:
      An extracted string from the RSS summary record.
    """
    # Infer from URL.
    parsed_url = urlparse(url)

    # Brunch RSS URLs e.g. https://brunch.co.kr/rss/@@iDz
    if parsed_url.hostname.endswith("brunch.co.kr") and "rss/@@" in url:
        return "RSS"

    # Infer from content.
    soup = BeautifulSoup(content, "xml")

    if soup.rss:
        return "RSS"
    elif soup.feed:
        # Could be more stable to check xmlns in
        #   <feed xmlns="http://www.w3.org/2005/Atom"...
        return "ATOM"
    else:
        return "UNKNOWN"

class FeedReaderFactory:
    """FeedReaderFactory class to return a feed reader.

    FeedReaderFactory creates a feed reader by feed type.

    Attributes:
      ...
    """
    # pylint: disable=unused-argument
    def get_reader(self, feed_type, url, feed_content=""):
        """Returns a feed reader object by feed type.

        Args:
          feed_type: The type of the feed.
          url: The feed URL.
          feed_content: The content of the feed.

        Returns:
          A feed reader object.
        """
        if feed_type == "RSS":
            return RssReader(feed_content=feed_content)
        elif feed_type == "ATOM":
            return AtomReader(feed_content=feed_content)
        elif feed_type == "SITEMAP":
            # Not implemented.
            return None
        else:
            return None
