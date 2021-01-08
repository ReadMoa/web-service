"""RSS Crawling tool.

Fetches RSS feeds listed in feeds.txt and insert new entries from the feeds
to the post table.

  Typical usage example:
  $ PYTHONPATH=./ python3 tools/rss_crawler/main.py
"""
from datetime import datetime, timezone
import logging
import os
import time

from dateutil.parser import parse
from bs4 import BeautifulSoup
import requests
from util import url as url_util
from util.post import Post
from util.post_db import PostDB

# Uncomment to output logging messages.
#import sys
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

RSS_FEED_FILE = "feeds.txt"
MAX_SUMMARY_LENGTH = 150
DATABASE_MODE = "prod"
MAX_NUM_RECORDS_TO_READ_PER_FEED = 1
AGE_LIMIT_FOR_PAGE = 86400  # seconds

post_db = PostDB(DATABASE_MODE)

def read_feed_file(feed_filepath):
    """Parses a feed list file and returns a list of feed URLs.

    Args:
      feed_filepath: A path to the file that contains a list of RSS feeds.

    Returns:
      A list of RSS feed URLs.
    """
    urls = []

    with open(feed_filepath) as feed_file:
        content = feed_file.readlines()

    for line in content:
        line = line.strip()
        if line == '' or line[0] == '#':
            continue
        urls.append(line)

    return urls

def fetch_rss(url):
    """Fetch RSS document from the given URL.

    Args:
      url: URL for RSS XML document.

    Returns:
      The content of RSS document.
    """
    rss_doc = requests.get(url)

    if rss_doc.status_code != 200:
        logger.warning(
                "Failed to fetch with Response Code %d for %s",
                rss_doc.status_code, rss_doc.url)

    return rss_doc.content

def read_rss(rss_content):
    """Parses RSS XML content and returns a list of entries.

    Parses an input RSS XML content and returns a list of content entries.

    Args:
      rss_content: A text string of RSS XML content.

    Returns:
      A list of dictionaries mapping attribute names to values.

      [{'title': 'foo', 'link': 'https://example.com/'},
       {'title': 'bar', 'link': 'https://example.com/another'}
      ]
    """
    soup = BeautifulSoup(rss_content, "xml")

    content_list = []
    num_entries = 0
    if soup.rss:
        for i in soup.findAll("item"):
            #DEBUG
            logger.info("RSS LINK: %s", i.link)

            url = i.link.text
            if not url:
                continue

            # TODO: Remove this limit when there is a solution to display for
            #       Naver blog image.
            if (url.startswith("https://blog.naver.com")
                or url.startswith("http://blog.naver.com")):
                continue

            updated = ''
            if i.find("pubDate"):
                updated = i.find("pubDate").get_text()                
                age = int((datetime.now(timezone.utc) - parse(updated)).total_seconds())
                if age > AGE_LIMIT_FOR_PAGE:
                    logger.info("Too old - %s, %ds ago", updated, age)
                    continue
            author = ""
            if not i.author:
                author = i.find("dc:creator").get_text()

            key = url_util.url_to_hashkey(url)
            if post_db.lookup(key):
                continue

            num_entries += 1
            content_list.append({
                "key": key,
                "title": i.title.text,
                "updated": updated,
                "link": url,
                "author": author,
                "summary": i.description.text,
                "main_image": fetch_main_image_link(url),
                })

            if num_entries > MAX_NUM_RECORDS_TO_READ_PER_FEED:
                break
    elif soup.feed:
        for i in soup.find_all("entry"):
            url = i.find("link")["href"]
            # TODO: Remove this limit when there is a solution to display for
            #       Naver blog image.
            if (url.startswith("https://blog.naver.com")
                or url.startswith("http://blog.naver.com")):
                continue

            key = url_util.url_to_hashkey(url)
            if post_db.lookup(key):
                continue

            updated = ''
            if i.find("pubDate"):
                updated = i.find("pubDate").get_text()
                age = int((datetime.now(timezone.utc) - parse(updated)).total_seconds())
                if (age > AGE_LIMIT_FOR_PAGE):
                    logger.info("Too old - %s, %ds ago", updated, age)
                    continue

            num_entries += 1
            content_list.append({
                "key": key,
                "title": i.find("title").get_text(),
                "updated": i.find("updated").get_text(),
                "link": url,
                "author": i.find("author").find("name").get_text(),
                "summary": i.find("summary").get_text(),
                "main_image": fetch_main_image_link(url),
                })

            # TODO: Remove this limit when the test is done.
            if num_entries > MAX_NUM_RECORDS_TO_READ_PER_FEED:
                break

    logger.info("Number of entries: %d", len(content_list))
    return content_list

def extract_from_summary(rss_summary_text):
    """Extracts summary text from a RSS summary record.

    Truncates if the text exceeds the threshold.

    Args:
      rss_summary_text: A text from <summary>...</summary>

    Returns:
      An extracted string from the RSS summary record.
    """
    summary_soup = BeautifulSoup(rss_summary_text, "html.parser")
    summary = ""
    for text in summary_soup.find_all(text=True):
        summary += "{} ".format(text)
        if len(summary) > MAX_SUMMARY_LENGTH:
            break

    logger.info("Extracted summary: %s", summary[:MAX_SUMMARY_LENGTH])
    return summary[:MAX_SUMMARY_LENGTH]

def fetch_main_image_link(page_url):
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

def add_content_to_database(parsed_content):
    """Add the input content to the database.

    Args:
      parsed_content: A list of dictionaries that contain meta data.

    Retruns:
      N/A
    """
    for record in parsed_content:
        post = Post(post_url=record["link"],
                title=record["title"],
                main_image_url=record["main_image"],
                description=extract_from_summary(record["summary"]))
        post_db.insert(post)

def main():
    """Main entry point.

    Reads and parses RSS feeds. Insert new entries into the post database.

    Args:
        N/A
    """
    feed_path = os.path.join(os.path.dirname(__file__), RSS_FEED_FILE)
    for feed_url in read_feed_file(feed_path):
        print("RSS processing started for ", feed_url)
        rss_content = fetch_rss(feed_url)
        parsed_content = read_rss(rss_content)
        for record in parsed_content:
            logger.info(
                "Incoming link: Key - %s, Main image - %s",
                record["key"], record["main_image"])
        add_content_to_database(parsed_content)

        print("RSS processing completed for ", feed_url)
    print("The full RSS import completed.")


if __name__ == "__main__":
    main()
