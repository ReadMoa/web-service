"""Reset feed tables in the backend database.

Drop tables and recreate them.

  Typical usage example:
  $ reset_feed_tables.py -m <mode: prod, dev, test(default)> -d <dryrun: true, false>
"""
import getopt
import logging
import sys

import sqlalchemy
from util import database

logger = logging.getLogger()

def create_tables(db_instance, mode, dryrun):
    """Creates all the tables in the database at 'mode'.

    Creates 'feeds' and 'feed_items' tables.

    Args:
        db_instance: a database instance.
        mode: prod/dev/test mode.
        dryrun: dryrun doesn't execute quries.

    Returns:
        N/A

    Raises:
        N/A
    """
    # Create tables (if they don't already exist)
    with db_instance.connect() as conn:
        # Create posts_serving if not exist.
        stmt = sqlalchemy.text("""
  CREATE TABLE IF NOT EXISTS {mode}_feeds (
    url_key CHAR(24) NOT NULL, 
    url VARCHAR(2084) NOT NULL, 
    title VARCHAR(128),
    label VARCHAR(255),
    description VARCHAR(2048), 
    language VARCHAR(6),
    changerate INT,
    generator VARCHAR(64),
    feed_type VARCHAR(8),
    popularity INT,
    first_fetched_time DATETIME,
    latest_fetched_time DATETIME,
    latest_item_url VARCHAR(2084),
    latest_item_title VARCHAR(128),
    PRIMARY KEY(url_key) 
  );
            """.format(mode=mode)
        )

        if dryrun:
            print("SQL query to execute: \n%s" % stmt)
        else:
            print("Executing the following command: \n%s" % stmt)
            conn.execute(stmt)

        # Create feed_items if not exist.
        stmt = sqlalchemy.text("""
  CREATE TABLE IF NOT EXISTS {mode}_feed_items (
    url_key CHAR(24) NOT NULL, 
    url VARCHAR(2084) NOT NULL, 
    feed_url_key CHAR(24) NOT NULL, 
    published_date DATETIME,
    PRIMARY KEY(url_key),
    FOREIGN KEY (feed_url_key) REFERENCES {mode}_feeds(url_key)
  );
            """.format(mode=mode)
        )

        if dryrun:
            print("SQL query to execute: \n%s" % stmt)
        else:
            print("Executing the following command: \n%s" % stmt)
            conn.execute(stmt)

def drop_tables(db_instance, mode, dryrun):
    """Drops all the tables in the database at 'mode'.

    Args:
        db_instance: a database instance.
        mode: prod/dev/test mode.
        dryrun: dryrun doesn't execute quries.

    Returns:
        N/A

    Raises:
        N/A
    """
    with db_instance.connect() as conn:
        stmt = sqlalchemy.text(
                "  DROP TABLE IF EXISTS {mode}_feeds;".format(mode=mode))
        if dryrun:
            print("SQL query to execute: \n%s" % stmt)
        else:
            print("Executing the following command: \n%s" % stmt)
            conn.execute(stmt)

        stmt = sqlalchemy.text(
                "  DROP TABLE IF EXISTS {mode}_feed_items;".format(mode=mode))
        if dryrun:
            print("SQL query to execute: \n%s" % stmt)
        else:
            print("Executing the following command: \n%s" % stmt)
            conn.execute(stmt)

def main(argv):
    """Main entry point.

    Delete tables and recreate them.

    Args:
        --mode: {prod, dev} prod/dev mode for a table set.
        --dryrun: {true, false} dryrun doesn't execute the queries.
    """
    mode = "test"
    dryrun = True

    try:
        opts, _ = getopt.getopt(argv,"hm:d:",["mode=","dryrun="])
    except getopt.GetoptError:
        # pylint: disable=line-too-long
        print("reset_post_tables.py -m <mode: prod, dev, test(default)> -d <dryrun: true(default), false>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("reset_post_tables.py -m <mode: prod, dev, test(default)> -d <dryrun: true(default), false>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev", "test"):
                print("Unknown 'mode': %s", mode)
                sys.exit(2)
        elif opt in ("-d", "--dryrun"):
            dryrun_arg = arg
            if dryrun_arg not in ("true", "false"):
                dryrun = True
                print("Unknown 'dryrun': %s (hint: case sensitive), run as dryrun.", dryrun_arg)
            else:
                dryrun = (dryrun_arg == "true")

    print("Refreshing the database started.")

    db_instance = database.init_connection_engine()
    drop_tables(db_instance, mode, dryrun)
    create_tables(db_instance, mode, dryrun)

    print("Refreshing the database completed.")

if __name__ == "__main__":
    main(sys.argv[1:])
