"""FeedReaderFactory and feed readers

  FeedReaderFactory creates a feed reader by a feed type.

  Typical usage example:

  from util.feed_reader_factory import FeedReaderFactory

  reader = FeedReaderFactory().get_reader(
      feed_type=feed_type, url=url, feed_content=feed.content)
  items = reader.read(count=10)
"""
import logging
import time

from bs4 import BeautifulSoup, Comment

import requests

logger = logging.getLogger()

MAX_NUM_RECORDS_TO_READ_PER_FEED = 10000
MAX_SUMMARY_LENGTH = 150

def fetch_main_image_from_post(page_url):
    """Fetch the main image link from the input page.

    This involves calling external web servers.

    Args:
      page_url: The document URL (can be a frameset document).

    Returns:
      Fetch a main image URL (og:image for now).
    """
    source_code = requests.get(page_url).text
    main_soup = BeautifulSoup(source_code, "html.parser")

    # TODO: Improve this to avoid calling inefficient sleeps.
    time.sleep(2)

    # Crawl and parse a webpage.
    if (page_url.startswith("https://blog.naver.com")
        or page_url.startswith("http://blog.naver.com")):
        main_frame_url = main_soup.find(id="mainFrame")["src"]
        main_frame_url = "https://blog.naver.com" + main_frame_url
        logger.info("Naver blog's main frame: %s", main_frame_url)

        main_frame_source_code = requests.get(main_frame_url).text
        main_soup = BeautifulSoup(main_frame_source_code, "html.parser")

        # TODO: Improve this to avoid calling inefficient sleeps.
        time.sleep(1)

    main_image = ""
    for each_text in main_soup.findAll("meta"):
        if each_text.get("property") == "og:image":
            main_image = each_text.get("content")
            logger.info("Extracted main image URL: %s", main_image)
            break

    return main_image


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


class FeedItem:
    """FeedItem to hold an item from a feed.

    Attributes:
      url: The URL of an item.
      title: The title of an item.
      description: The description.
      published_date: The published date of an item.
      author: The author of an item.
    """
    def __init__(
        self, url, title, description, published_date, author):
        self.url = url
        self.title = title
        self.description = description
        self.published_date = published_date
        self.author = author

# <rss version="2.0">
#   <channel>
class RssReader:
    """RssReader parses an RSS feed.

    Attributes:
      feed_content: The content of the feed.
    """

    def __init__(self, feed_content):
        self.feed_content = feed_content

    def read(self, count=1):
        """Parses the RSS feed and returns 'count' number of items.

        Args:
          count: the number of items to return.

        Returns:
          A list of items parsed from the feed.
        """
        soup = BeautifulSoup(self.feed_content, "xml")
        items = []
        num_entries = 0
        for i in soup.findAll("item"):
            if num_entries >= count:
                break

            url = i.link.text
            if not url:
                raise ValueError("Empty <link>")

            updated = ""
            if i.find("pubDate"):
                updated = i.find("pubDate").get_text()

            author = ""
            if not i.author:
                author = i.find("dc:creator").get_text()

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

    def read(self, count=1):
        """Parses the ATOM feed and returns 'count' number of items.

        Args:
          count: the number of items to return.

        Returns:
          A list of items parsed from the feed.
        """
        soup = BeautifulSoup(self.feed_content, "xml")
        items = []
        num_entries = 0
        for i in soup.find_all("entry"):
            if num_entries >= count:
                break

            url = i.find("link")["href"]

            updated = ''
            if i.find("updated"):
                updated = i.find("updated").get_text()
            author = i.find("author").find("name").get_text()
            description = extract_from_post(i.find("summary").get_text())
            title = i.find("title").get_text()

            items.append(FeedItem(
                url=url, title=title, description=description,
                published_date=updated, author=author))
            num_entries += 1

        return items


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
