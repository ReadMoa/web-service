"""Reset tables in the backend database.

Drop tables and recreate them. Add a record to each table.

  Typical usage example:
  $ reset_database.py -m <mode: prod, dev> -d <dryrun: true, false>
"""

import datetime
import getopt
import logging
import sys

import sqlalchemy
from util import database

logger = logging.getLogger()

def create_tables(db_instance, mode, dryrun):
    """Creates all the tables in the database at 'mode'.

    Creates 'posts_serving', 'users', and 'comments' tables. Insert a record
    to each table.

    Args:
        db_instance: a database instance.
        mode: prod/dev mode.
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
            CREATE TABLE IF NOT EXISTS {mode}_posts_serving (
            post_url_hash CHAR(24) NOT NULL, 
            post_url  TEXT(2084) NOT NULL, 
            submission_time DATETIME, 
            title TEXT(1024), 
            main_image_url TEXT(2084), 
            description TEXT(2048), 
            user_display_name VARCHAR(100), 
            user_email VARCHAR(255), 
            user_photo_url TINYTEXT, 
            user_provider_id VARCHAR(100), 
            user_id VARCHAR(100), 
            featured_comment TEXT(2048), 
            featured_comment_submission_time DATETIME, 
            featured_comment_user_display_name VARCHAR(100), 
            featured_comment_user_email VARCHAR(255), 
            featured_comment_user_photo_url TINYTEXT, 
            featured_comment_user_id VARCHAR(100), 
            PRIMARY KEY(post_url_hash) 
            );
            """.format(mode=mode)
        )

        if dryrun:
            print("SQL query to execute: \n%s" % stmt)
        else:
            print("Executing the following command: \n%s" % stmt)
            conn.execute(stmt)

        # Create comments if not exist.
        stmt = sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS {mode}_comments (
            post_url TINYTEXT, 
            comment TEXT(2048), 
            submission_time DATETIME, 
            user_id VARCHAR(100), 
            user_display_name VARCHAR(100), 
            user_photo_url TINYTEXT, 
            user_email VARCHAR(255) 
            );
            """.format(mode=mode)
        )

        if dryrun:
            print("SQL query to execute: \n%s" % stmt)
        else:
            print("Executing the following command: \n%s" % stmt)
            conn.execute(stmt)

        # Create users if not exist.
        stmt = sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS {mode}_users (
            user_id VARCHAR(100), 
            user_display_name VARCHAR(100), 
            user_email VARCHAR(255), 
            user_photo_url TINYTEXT, 
            user_provider_id VARCHAR(100), 
            lastest_login_time DATETIME, 
            sign_up_time DATETIME 
            );
            """.format(mode=mode)
        )

        if dryrun:
            print("SQL query to execute: \n%s" % stmt)
        else:
            print("Executing the following command: \n%s" % stmt)
            conn.execute(stmt)

    stmt = sqlalchemy.text("""
        INSERT INTO {mode}_posts_serving (
          post_url_hash, post_url, submission_time, title, main_image_url, description, 
          user_display_name, user_email, user_photo_url, user_provider_id, user_id, 
          featured_comment, featured_comment_submission_time, 
          featured_comment_user_display_name, featured_comment_user_email, 
          featured_comment_user_photo_url, featured_comment_user_id) 
        VALUES (
          :post_url_hash, :post_url, :submission_time, :title, :main_image_url, :description, 
          :user_display_name, :user_email, :user_photo_url, :user_provider_id, :user_id, 
          :featured_comment, :featured_comment_submission_time, 
          :featured_comment_user_display_name, :featured_comment_user_email, 
          :featured_comment_user_photo_url, :featured_comment_user_id 
        )
        """.format(mode=mode)
    )

    if dryrun:
        print("SQL query to execute: \n%s" % stmt)
        return

    try:
        time_now = datetime.datetime.utcnow()
        with db_instance.connect() as conn:
            conn.execute(
                stmt, post_url_hash="deadbeafdeadbeafdeadbeaf",
                post_url="https://news.v.daum.net/v/20200816080119455", submission_time=time_now,
                title="美 입양한인 \"나를 잃어버린 부모 눈물의 나날 보내고 있을 것\"",
                # pylint: disable=line-too-long
                main_image_url="https://img1.daumcdn.net/thumb/S1200x630/?fname=https://t1.daumcdn.net/news/202008/16/yonhap/20200816080119500cqms.jpg",
                # pylint: disable=line-too-long
                description="(서울=연합뉴스) 왕길환 기자 = \"친부모와 가족이 제가 죽었다고 믿거나 저를 찾는 방법을 몰랐을까 봐 두렵습니다. 나이들수록 영영 부모님을 보지 못할 수도 있다는 생각에 눈물이 나고 슬퍼요.\" 미국 워싱턴주 시애틀에 사는 입양한인 에이미 카 배럿(한국명 오미숙·51) 씨는 친부모가 자신을 잃어버리고",
                user_display_name="어드민",
                user_email="admin@readmoa.net",
                user_photo_url="/chrome_icon.png",
                user_provider_id="test-id",
                user_id="user-id",
                featured_comment="안타까운 이야기네요.",
                featured_comment_submission_time=time_now,
                featured_comment_user_display_name="사용자",
                featured_comment_user_email="user@readmoa.net",
                featured_comment_user_photo_url="/chrome_icon.png",
                featured_comment_user_id="user-id")
    except db_instance.Error as ex:
        logger.exception(ex)

def drop_tables(db_instance, mode, dryrun):
    """Drops all the tables in the database at 'mode'.

    Args:
        db_instance: a database instance.
        mode: prod/dev mode.
        dryrun: dryrun doesn't execute quries.

    Returns:
        N/A

    Raises:
        N/A
    """
    with db_instance.connect() as conn:
        stmt = sqlalchemy.text(
                "DROP TABLE {mode}_posts_serving;".format(mode=mode))
        if dryrun:
            print("SQL query to execute: \n%s" % stmt)
        else:
            print("Executing the following command: \n%s" % stmt)
            conn.execute(stmt)

        stmt = sqlalchemy.text(
                "DROP TABLE {mode}_comments;".format(mode=mode))
        if dryrun:
            print("SQL query to execute: \n%s" % stmt)
        else:
            print("Executing the following command: \n%s" % stmt)
            conn.execute(stmt)

        stmt = sqlalchemy.text(
                "DROP TABLE {mode}_users;".format(mode=mode))
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
    mode = "dev"
    dryrun = True

    try:
        opts, _ = getopt.getopt(argv,"hm:d:",["mode=","dryrun="])
    except getopt.GetoptError:
        print("reset_database.py -m <mode: prod, dev(default)> -d <dryrun: true(default), false>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            # pylint: disable=line-too-long
            print("reset_database.py -m <mode: prod, dev(default)> -d <dryrun: true(default), false>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            if mode not in ("prod", "dev"):
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
