"""PostDB class definition.

  PostDB encapsualte interactions (lookup, scan, insert) with the posts table.

  Typical usage example:

  from post import Post
  from post_db import PostDB

  post_db = PostDB(mode = "dev")
  post = Post(
      post_url = "https://www.example.com/",
      title = "Test",
      main_image_url = "https://www.example.com/foo.png",
      description = "Bar")
  post_db.insert(post)
"""
import logging

import sqlalchemy
from util.database import init_connection_engine
from util.post import Post

# Max post index to return in scan().
MAX_POSTS_TO_START = 1000

logger = logging.getLogger()

class PostDB:
    """PostDB class to interact with the posts table.

    PostDB provides lookup, scan, insert operations for posts.

    Attributes:
      ...
    """
    def __init__(self, mode="dev"):
        self.db_instance = init_connection_engine()
        self.mode = mode

    def lookup(self, key):
        """Looks up a post from posts table with the input key.

        Args:
          key: A hash of a post URL.

        Returns:
          A Post instance with retrieved data from posts table or None.
        """
        post = None
        with self.db_instance.connect() as conn:
            # Execute the query and fetch all results
            returned_posts = conn.execute("""
                SELECT post_url_hash, post_url, post_author, post_published_date,
                    title, submission_time, main_image_url, description, 
                    user_display_name, user_email, user_photo_url, user_id, user_provider_id 
                FROM {mode}_posts_serving 
                where post_url_hash = '{key}'
                """.format(mode=self.mode, key=key)
            ).fetchall()

            if len(returned_posts) > 0:
                row = returned_posts[0]
                post = Post(
                    post_url=row[1], title=row[2], author=row[3],
                    published_date=row[4], submission_time=row[5],
                    main_image_url=row[6], description=row[7],
                    user_display_name=row[8], user_email=row[9],
                    user_photo_url=row[10], user_id=row[11],
                    user_provider_id=row[12])
        return post

    def scan(self, start_idx=0, count=10):
        """Scans posts table and resturns a list of Post instances.

        Posts of [start_idx, start_idx + count) records will be returned.

        Args:
          start_idx: The start index of the scan.
          count: # of posts to return

        Returns:
          A list of posts.
        """
        # pylint: disable=fixme
        # TODO: Can we change 'start' as an absolute position e.g. timestamp
        #       to make the result consistent even when there is a new item
        #       to posts_serving db.
        posts = []
        if start_idx < 0 or start_idx > MAX_POSTS_TO_START:
            logger.warning("start_idx is out of range: %d", start_idx)
            return posts  # Empty list

        if count < 0 or count > MAX_POSTS_TO_START:
            logger.warning("count is out of range: %d", count)
            return posts  # Empty list

        with self.db_instance.connect() as conn:
            # Execute the query and fetch all results
            recent_posts = conn.execute("""
                SELECT post_url_hash, post_url, title, post_author,
                    post_published_date, submission_time, main_image_url,
                    description, user_display_name, user_email, user_photo_url,
                    user_id, user_provider_id 
                FROM {mode}_posts_serving 
                ORDER BY submission_time DESC LIMIT {limit:d}
                """.format(mode=self.mode, limit=start_idx + count)
            ).fetchall()

            if len(recent_posts) > start_idx:
                for row in recent_posts[start_idx:]:
                    posts.append(
                        Post(
                            post_url=row[1], title=row[2], author=row[3],
                            published_date=row[4], submission_time=row[5],
                            main_image_url=row[6], description=row[7],
                            user_display_name=row[8], user_email=row[9],
                            user_photo_url=row[10], user_id=row[11],
                            user_provider_id=row[12]
                        )
                    )
        return posts

    def insert(self, post):
        """Insert a post record into posts table.

        Args:
          post: A Post instance.
        """
        if not post.is_valid():
            logger.error("Invalid post.")
            return

        stmt = sqlalchemy.text("""
            INSERT INTO {mode}_posts_serving 
            (post_url_hash, post_url, post_author, post_published_date,
            submission_time, title, main_image_url, description,
            user_id, user_display_name, user_email, user_photo_url,
            user_provider_id) 
            VALUES 
            (:url_hash, :url, :author, :published_date, :submission_time,
            :title, :main_image_url, :description, :user_id,
            :user_display_name, :user_email, :user_photo_url,
            :user_provider_id)
            """.format(mode=self.mode)
        )

        logger.info(stmt)

        try:
            with self.db_instance.connect() as conn:
                conn.execute(
                        stmt, url_hash=post.post_url_hash, url=post.post_url,
                        author=post.author, published_date=post.published_date,
                        submission_time=post.submission_time,
                        title=post.title, main_image_url=post.main_image_url,
                        description=post.description, user_id=post.user_id,
                        user_display_name=post.user_display_name,
                        user_email=post.user_email,
                        user_photo_url=post.user_photo_url,
                        user_provider_id=post.user_provider_id)
        except self.db_instance.Error as ex:
            logger.exception(ex)
            return

    def delete(self, key):
        """Deletes a post from posts table with the input key.

        Args:
          key: A hash of a post URL.
        """
        with self.db_instance.connect() as conn:
            conn.execute("""
                DELETE FROM {mode}_posts_serving 
                where post_url_hash = '{key}'
                """.format(mode=self.mode, key=key)
            )
