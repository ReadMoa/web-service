"""FeedDB class definition.

  FeedDB is an interface to Feed table, providing interactions (lookup,
  scan, insert) with the posts table.

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
import logging

import sqlalchemy
from util.database import init_connection_engine
from util.feed import Feed

logger = logging.getLogger()

class FeedDB:
    """FeedDB class to interact with the feeds table.

    FeedDB provides lookup, scan, insert operations for feeds.

    Attributes:
      ...
    """
    def __init__(self, mode="dev"):
        self.db_instance = init_connection_engine()
        self.mode = mode

    def lookup_feed(self, url_key):
        """Looks up a feed from feeds table with the input key.

        Args:
          url_key: A hash of a feed URL.

        Returns:
          A Feed instance with retrieved data from feeds table or None.
        """
        feed = None
        with self.db_instance.connect() as conn:
            # Execute the query and fetch all results
            returned_feeds = conn.execute("""
                SELECT url_key, url, title, changerate, feed_type, label,
                       language, description, generator, popularity,
                       first_fetched_time, latest_fetched_time, latest_item_url,
                       latest_item_title
                FROM {mode}_feeds
                where url_key = '{url_key}'
                """.format(mode=self.mode, url_key=url_key)
            ).fetchall()

            if len(returned_feeds) > 0:
                row = returned_feeds[0]
                feed = Feed(url_key=row[0], url=row[1], title=row[2],
                        changerate=row[3], feed_type=row[4], label=row[5],
                        language=row[6], description=row[7], generator=row[8],
                        popularity=row[9], first_fetched_time=row[10],
                        latest_fetched_time=row[11], latest_item_url=row[12],
                        latest_item_title=row[13])
        return feed

    def scan_feeds(self, start_idx=0, count=10):
        """Scans Feeds table and resturns a list of feeds.

        Recent feeds sorted by latest_fetched_time will be returned.
        [start_idx, start_idx + count) records will be returned.

        Args:
          start_idx: The start index of the scan.
          count: # of feeds to return

        Returns:
          A list of Feed instances.
        """
        feeds = []
        if start_idx < 0:
            logger.warning("start_idx is out of range: %d", start_idx)
            return feeds  # Empty list

        if count < 0:
            logger.warning("count is out of range: %d", count)
            return feeds  # Empty list

        with self.db_instance.connect() as conn:
            # Execute the query and fetch all results
            recent_feeds = conn.execute("""
                SELECT url_key, url, title, changerate, feed_type, label,
                       language, description, generator, popularity,
                       first_fetched_time, latest_fetched_time, latest_item_url,
                       latest_item_title
                FROM {mode}_feeds
                ORDER BY latest_fetched_time DESC LIMIT {limit:d}
                """.format(mode=self.mode, limit=start_idx + count)
            ).fetchall()

            if len(recent_feeds) > start_idx:
                for row in recent_feeds[start_idx:]:
                    feeds.append(Feed(
                        url_key=row[0], url=row[1], title=row[2],
                        changerate=row[3], feed_type=row[4], label=row[5],
                        language=row[6], description=row[7], generator=row[8],
                        popularity=row[9], first_fetched_time=row[10],
                        latest_fetched_time=row[11], latest_item_url=row[12],
                        latest_item_title=row[13]))

        return feeds

    def insert_feed(self, feed):
        """Insert a feed record into feeds table.

        Args:
          feed: A Feed instance.
        """
        if not feed.is_valid():
            logger.error("Invalid feed.")
            return

        stmt = sqlalchemy.text("""
            INSERT INTO {mode}_feeds
            (url_key, url, feed_type, title, changerate,  label,
            language, description, generator, popularity, first_fetched_time,
            latest_fetched_time, latest_item_url, latest_item_title)
            VALUES 
            (:url_key, :url, :feed_type, :title, :changerate, :label,
            :language, :description, :generator, :popularity,
            :first_fetched_time, :latest_fetched_time, :latest_item_url,
            :latest_item_title)
            """.format(mode=self.mode)
        )

        logger.info(stmt)

        try:
            with self.db_instance.connect() as conn:
                conn.execute(
                        stmt, url_key=feed.url_key, url=feed.url,
                        title=feed.title, changerate=feed.changerate,
                        feed_type=feed.feed_type, label=feed.label,
                        language=feed.language, description=feed.description,
                        generator=feed.generator, popularity=feed.popularity,
                        first_fetched_time=feed.first_fetched_time,
                        latest_fetched_time=feed.latest_fetched_time,
                        latest_item_url=feed.latest_item_url,
                        latest_item_title=feed.latest_item_title)
        except self.db_instance.Error as ex:
            logger.exception(ex)
            return

    def delete_feed(self, url_key):
        """Deletes a feed from feeds table with the input key.

        Args:
          url_key: A hash of a feed URL.
        """
        with self.db_instance.connect() as conn:
            conn.execute("""
                DELETE FROM {mode}_feeds
                where url_key = '{url_key}'
                """.format(mode=self.mode, url_key=url_key)
            )
