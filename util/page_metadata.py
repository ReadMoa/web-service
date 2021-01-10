"""Utility functions for metadata on a page

  Typical usage example:

  from util.page_metadata import fetch_main_image_from_post

  main_image_url = fetch_main_image_from_post("https://www.example.com/")
  print("Main image URL: ", main_image_url)
"""
import logging
import time

from bs4 import BeautifulSoup
import requests

logger = logging.getLogger()

# Aritificial delay for fetching web resources to avoid hammering web servers.
FETCH_DELAY_SECS = 1

def fetch_main_image_from_post(page_url):
    """Fetch the main image link from the input page.

    This involves calling external web servers.

    Args:
      page_url: The document URL (can be a frameset document).

    Returns:
      Fetch a main image URL (og:image for now).
    """
    time.sleep(FETCH_DELAY_SECS)
    source_code = requests.get(page_url).text
    main_soup = BeautifulSoup(source_code, "html.parser")

    # Crawl and parse a webpage.
    if (page_url.startswith("https://blog.naver.com")
        or page_url.startswith("http://blog.naver.com")):
        main_frame_url = main_soup.find(id="mainFrame")["src"]
        main_frame_url = "https://blog.naver.com" + main_frame_url
        logger.info("Naver blog's main frame: %s", main_frame_url)

        time.sleep(FETCH_DELAY_SECS)
        main_frame_source_code = requests.get(main_frame_url).text
        main_soup = BeautifulSoup(main_frame_source_code, "html.parser")

    main_image = ""
    for each_text in main_soup.findAll("meta"):
        if each_text.get("property") == "og:image":
            main_image = each_text.get("content")
            logger.info("Extracted main image URL: %s", main_image)
            break

    return main_image