"""RSS Crawling tool.

Fetches RSS feeds listed in feeds.txt and insert new entries from the feeds
to the post table.

  Typical usage example:
  $ PYTHONPATH=./ python3 tools/rss_crawler/main.py
"""
import datetime
import logging
import os
import time

import requests
import sqlalchemy
from bs4 import BeautifulSoup
from util import database
from util import url as url_util

# Uncomment to output logging messages.
#import sys
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

RSS_FEED_FILE = "feeds.txt"
MAX_SUMMARY_LENGTH = 150
DATABASE_MODE = "prod"

# The SQLAlchemy engine will help manage interactions, including automatically
# managing a pool of connections to your database
db_instance = database.init_connection_engine()

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
            if not i.pubDate:
                updated = i.pubdate.text
            else:
                updated = i.pubDate.text

            author = ""
            if not i.author:
                author = i.find("dc:creator").get_text()

            num_entries += 1
            content_list.append({
                "key": url_util.url_to_hashkey(url),
                "title": i.title.text,
                "updated": updated,
                "link": url,
                "author": author,
                "summary": i.description.text,
                "main_image": fetch_main_image_link(url),
                })

            # TODO: Remove this limit when the test is done.
            if num_entries > 3:
                break

    elif soup.feed:
        for i in soup.find_all("entry"):
            url = i.find("link")["href"]
            # TODO: Remove this limit when there is a solution to display for
            #       Naver blog image.
            if (url.startswith("https://blog.naver.com")
                or url.startswith("http://blog.naver.com")):
                continue

            num_entries += 1
            content_list.append({
                "key": url_util.url_to_hashkey(url),
                "title": i.find("title").get_text(),
                "updated": i.find("updated").get_text(),
                "link": url,
                "author": i.find("author").find("name").get_text(),
                "summary": i.find("summary").get_text(),
                "main_image": fetch_main_image_link(url),
                })

            # TODO: Remove this limit when the test is done.
            if num_entries > 3:
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
    stmt = sqlalchemy.text("""
        INSERT INTO {mode}_posts_serving 
          (post_url_hash, post_url, submission_time, user_id, 
           user_email, title, main_image_url, description) 
        VALUES 
         (:url_hash, :url, :time_cast, :userid, 
          :user_email, :title, :main_image, :description)
        """.format(mode=DATABASE_MODE)
    )

    try:
        with db_instance.connect() as conn:
            for record in parsed_content:
                url_hash = record["key"]
                url = record["link"]
                title = record["title"]
                description = extract_from_summary(record["summary"])
                main_image = record["main_image"]
                time_cast = datetime.datetime.utcnow()
                user_email = "admin@readmoa.net"
                userid = "user-id"
                # TODO: Add 'author' field in the database and use this info.
                _author = record["author"]

                # Check if the post already exists.
                post = conn.execute("""
                    SELECT post_url_hash, post_url, submission_time 
                    FROM {mode}_posts_serving 
                    WHERE post_url_hash = '{key}'
                    """.format(mode=DATABASE_MODE, key=record["key"] )
                ).fetchall()

                if len(post) > 0:
                    post_url = post[0][1]
                    logging.info("Already exists in posts_serving: %s",
                            post_url)
                    continue

                conn.execute(
                        stmt, url_hash=url_hash, url=url,
                        time_cast=time_cast, userid=userid,
                        user_email=user_email,
                        title=title, main_image=main_image,
                        description=description)
                logger.info("Record to DB: '%s'", title)
    except db_instance.Error as ex:
        logger.exception(ex)

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
