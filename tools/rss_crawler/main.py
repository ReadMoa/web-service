from bs4 import BeautifulSoup
import logging
import os
import requests

logger = logging.getLogger()

RSS_FEED_FILE = "feeds.txt"

def read_feed_file(feed_filepath):
    """Parses a feed list file and returns a list of feed URLs.

    Args:
      feed_filepath: A path to the file that contains a list of RSS feeds.

    Returns:
      A list of RSS feed URLs.
    """
    urls = []

    with open(feed_filepath) as f:
        content = f.readlines()

    for line in content:
        if line[0] == '#':
            continue
        urls.append(line.strip())

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
    soup = BeautifulSoup(rss_content, "lxml")
    
    content_list = []
    num_entries = 0
    for i in soup.find_all("entry"):
        num_entries += 1
        content_list.append({
            "title": i.find("title").get_text(),
            "updated": i.find("updated").get_text(),
            "link": i.find("link")["href"],
            "author": i.find("author").find("name").get_text(),
            "summary": i.find("summary").get_text()
            })
    
    logger.info("Number of entries: %d", len(content_list));
    return content_list

def main():
    feed_path = os.path.join(os.path.dirname(__file__), RSS_FEED_FILE)
    for feed_url in read_feed_file(feed_path):
        rss_content = fetch_rss(feed_url)
        parsed_content = read_rss(rss_content)
        for record in parsed_content:
            print("Title: ", record["title"])
    

if __name__ == "__main__":
    main()
