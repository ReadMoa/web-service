"""FeedReaderFactory and feed readers

  FeedReaderFactory creates a feed reader by a feed type.

  Typical usage example:

  from util.feed_reader_factory import FeedReaderFactory

  reader = FeedReaderFactory().get_reader(
      feed_type=feed_type, url=url, feed_content=feed.content)
  items = reader.read(count=10)
"""
import html
import logging
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from dateutil.parser import parse
from util.feed import FeedItem

logger = logging.getLogger()

MAX_NUM_RECORDS_TO_READ_PER_FEED = 10000
MAX_SUMMARY_LENGTH = 150

def extract_from_post(html_text):
    """Extracts summary text from a RSS summary record.

    Truncates if the text exceeds the threshold.

    Args:
      html: A text in html.

    Returns:
      An extracted string from the RSS summary record.
    """
    summary_soup = BeautifulSoup(html_text, "html.parser")
    summary = ""
    if summary_soup.body:
        summary_soup = summary_soup.body

    for text in summary_soup.find_all(text=True):
        unescaped_text = html.unescape(text)
        summary += "{} ".format(unescaped_text)
        if len(summary) > MAX_SUMMARY_LENGTH:
            break

    logger.info("Extracted summary: %s", summary[:MAX_SUMMARY_LENGTH])
    return summary[:MAX_SUMMARY_LENGTH]

def extract_from_cdata(txt):
    """Extracts text from CDATA.

    Args:
      txt: A CDATA string. e.g. <![CDATA[Test]]>

    Returns:
      An extracted string from the input CDATA string.
    """
    result = ""
    soup = BeautifulSoup(txt, "xml")
    for cdata in soup.findAll(text=True):
        if isinstance(cdata, BeautifulSoup.CData):
            result += "{}".format(html.unescape(repr(cdata)))
        else:
            result += "{}".format(html.unescape(cdata))
    return result

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
        if channel.description:
            self.description = channel.description.text
        if channel.language:
            self.language = channel.language.text
        if channel.generator:
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
                author = html.unescape(i.find("author").get_text())
            elif i.find("dc:creator"):
                # Example: <dc:creator><![CDATA[Test Lee]]></dc:creator>
                author_src_text = i.find("dc:creator").get_text().strip()
                if author_src_text.startswith("<![CDATA["):
                    author = extract_from_cdata(author_src_text)
                else:
                    author = author_src_text

            title = html.unescape(i.title.text)
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
            author = html.unescape(i.find("author").find("name").get_text())
            description = extract_from_post(i.find("summary").get_text())
            title = html.unescape(i.find("title").get_text())

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
