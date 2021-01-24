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
from datetime import timedelta
import logging

import sqlalchemy
from util.database import Database
from util.feed import Feed

logger = logging.getLogger()
MAX_CHANGERATE = 14 * 86400

def calculate_changerate(events):
    """Calculate the changerate from feed event logs.

    Args:
        events: A list of events. An event data looks:
            {
                "url_key"
                "fetched_time"
                "feed_updated"
                "newest_post_published_date"
                "previous_changerate"
                "previous_scheduled_fetch_time"
            }

    Returns:
        The calculated changerate in seconds.
    """
    # A simple algorithm to calculate a changerate.
    # changerate = (latest feed fetched time) - (published time of the
    #               newest post)
    events.sort(key=lambda e:e["fetched_time"], reverse=True)

    duration = events[0]["fetched_time"] - events[0]["newest_post_published_date"]

    if duration.seconds <= 0:
        return 86400   # default: 1 day
    elif duration.seconds > MAX_CHANGERATE:
        return MAX_CHANGERATE
    else:
        return duration.seconds

class FeedDB:
    """FeedDB class to interact with the feeds table.

    FeedDB provides lookup, scan, insert operations for feeds.

    Attributes:
      ...
    """
    def __init__(self, mode="dev"):
        self.db_instance = Database.get_instance().connection
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
                       latest_item_title, scheduled_fetch_time
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
                        latest_item_title=row[13],
                        scheduled_fetch_time=row[14])
        return feed

    def update_changerate(self, url_key):
        """Updates the changerate of a feed.

        Call this method after a new log event for a feed completed.
        It will calculate a new changerate and update Feeds table.

        Args:
          url_key: A hash of a feed URL.
        """
        with self.db_instance.connect() as conn:
            log_db = FeedFetchLogDB(self.mode)
            events = log_db.scan(url_key, count=10)
            changerate = calculate_changerate(events)

            # Sort events in reverse chronological order.
            events.sort(key=lambda e:e["fetched_time"], reverse=True)
            latest_fetched_time = events[0]["fetched_time"]
            scheduled_fetch_time = latest_fetched_time + timedelta(seconds=changerate)
            logger.info(
                "New changerate for [%s]: %d (latest fetch:%s)",
                url_key, changerate, latest_fetched_time)
            conn.execute("""
                UPDATE {mode}_feeds
                SET
                  changerate = {changerate},
                  latest_fetched_time = '{latest_fetched_time}',
                  scheduled_fetch_time = '{scheduled_fetch_time}'
                WHERE url_key = '{url_key}'
                """.format(
                    mode=self.mode, changerate=changerate,
                    latest_fetched_time=latest_fetched_time,
                    scheduled_fetch_time=scheduled_fetch_time,
                    url_key=url_key)
            )

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
                       latest_item_title, scheduled_fetch_time
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
                        latest_item_title=row[13],
                        scheduled_fetch_time=row[14]))

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
            latest_fetched_time, latest_item_url, latest_item_title,
            scheduled_fetch_time)
            VALUES 
            (:url_key, :url, :feed_type, :title, :changerate, :label,
            :language, :description, :generator, :popularity,
            :first_fetched_time, :latest_fetched_time, :latest_item_url,
            :latest_item_title, :scheduled_fetch_time)
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
                        latest_item_title=feed.latest_item_title,
                        scheduled_fetch_time=feed.scheduled_fetch_time)
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


class FeedFetchLogDB:
    """FeedFetchLogDB class to interact with feed_fetch_log table.

    FeedDB provides log, scan operations for feed fetching events.

    Attributes:
      ...
    """
    def __init__(self, mode="dev"):
        self.db_instance = Database.get_instance().connection
        self.mode = mode

    def log(
        self, url_key, fetched_time, feed_updated, newest_post_published_date,
        previous_changerate, previous_scheduled_fetch_time):
        """Logs a fetching event for a feed.

        Args:
          url_key (string): A hash of a feed URL.
          fetched_time (datetime): The time the fetching event happened.
          feed_updated (bool): Is the feed updated when it was fetched?
          newest_post_published_date (datetime): The published date of the
            newest post when it was fetched.
          previous_changerate (int): The estimated changerate when the event
            happened.
          previous_scheduled_fetch_time (DATETIME): The next scheduled fetch
            time when the event happened.

        Returns:
          True if successful.
        """
        stmt = sqlalchemy.text("""
            INSERT INTO {mode}_feed_fetch_log
            (url_key, fetched_time, feed_updated, newest_post_published_date,
             previous_changerate, previous_scheduled_fetch_time)
            VALUES 
            (:url_key, :fetched_time, :feed_updated,
             :newest_post_published_date, :previous_changerate,
             :previous_scheduled_fetch_time)
            """.format(mode=self.mode)
        )

        logger.info(stmt)

        try:
            with self.db_instance.connect() as conn:
                conn.execute(
                        stmt, url_key=url_key, fetched_time=fetched_time,
                        feed_updated=feed_updated,
                        newest_post_published_date=newest_post_published_date,
                        previous_changerate=previous_changerate,
                        previous_scheduled_fetch_time=previous_scheduled_fetch_time)
        except self.db_instance.Error as ex:
            logger.exception(ex)
            return

    def scan(self, url_key, count=100):
        """Scan logs for a feed.

        Args:
          url_key (string): A hash of a feed URL.
          count (int): # of log events to return (reverse chronological).

        Returns:
          A list of logs.
        """
        events = []
        with self.db_instance.connect() as conn:
            # Execute the query and fetch all results
            recent_events = conn.execute("""
                SELECT url_key, fetched_time, feed_updated,
                  newest_post_published_date,
                  previous_changerate, previous_scheduled_fetch_time
                FROM {mode}_feed_fetch_log
                where url_key = '{url_key}'
                ORDER BY fetched_time DESC LIMIT {limit:d}
                """.format(mode=self.mode, url_key=url_key, limit=count)
            ).fetchall()

            for row in recent_events:
                events.append({
                    "url_key":row[0], "fetched_time":row[1],
                    "feed_updated":row[2],
                    "newest_post_published_date":row[3],
                    "previous_changerate":row[4],
                    "previous_scheduled_fetch_time":row[5]})
        return events
