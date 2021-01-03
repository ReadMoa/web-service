"""A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()
"""
import logging
import os

import sqlalchemy

# The SQLAlchemy engine will help manage interactions, including automatically
# managing a pool of connections to your database
def init_connection_engine():
    db_config = {
        # [START cloud_sql_mysql_sqlalchemy_limit]
        # Pool size is the maximum number of permanent connections to keep.
        "pool_size": 5,
        # Temporarily exceeds the set pool_size if no connections are available.
        "max_overflow": 2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # [END cloud_sql_mysql_sqlalchemy_limit]
        # [START cloud_sql_mysql_sqlalchemy_backoff]
        # SQLAlchemy automatically uses delays between failed connection attempts,
        # but provides no arguments for configuration.
        # [END cloud_sql_mysql_sqlalchemy_backoff]
        # [START cloud_sql_mysql_sqlalchemy_timeout]
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        "pool_timeout": 30,  # 30 seconds
        # [END cloud_sql_mysql_sqlalchemy_timeout]
        # [START cloud_sql_mysql_sqlalchemy_lifetime]
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # reestablished
        "pool_recycle": 1800,  # 30 minutes
        # [END cloud_sql_mysql_sqlalchemy_lifetime]
    }

    if os.environ.get("DB_HOST"):
        return init_tcp_connection_engine(db_config)
    else:
        return init_unix_connection_engine(db_config)

def init_tcp_connection_engine(db_config):
    # [START cloud_sql_mysql_sqlalchemy_create_tcp]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_host = os.environ["DB_HOST"]

    # Extract host and port from db_host
    host_args = db_host.split(":")
    db_hostname, db_port = host_args[0], int(host_args[1])

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            host=db_hostname,  # e.g. "127.0.0.1"
            port=db_port,  # e.g. 3306
            database=db_name,  # e.g. "my-database-name"
        ),
        # ... Specify additional properties here.
        # [END cloud_sql_mysql_sqlalchemy_create_tcp]
        **db_config
        # [START cloud_sql_mysql_sqlalchemy_create_tcp]
    )
    # [END cloud_sql_mysql_sqlalchemy_create_tcp]

    return pool

def init_unix_connection_engine(db_config):
    # [START cloud_sql_mysql_sqlalchemy_create_socket]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            database=db_name,  # e.g. "my-database-name"
            query={
                "unix_socket": "{}/{}".format(
                    db_socket_dir,  # e.g. "/cloudsql"
                    cloud_sql_connection_name)  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
            }
        ),
        # ... Specify additional properties here.

        # [END cloud_sql_mysql_sqlalchemy_create_socket]
        **db_config
        # [START cloud_sql_mysql_sqlalchemy_create_socket]
    )
    # [END cloud_sql_mysql_sqlalchemy_create_socket]

    return pool

def create_tables(db):
    # Create tables (if they don't already exist)
    with db.connect() as conn:
        # clean up all the tables.
        #conn.execute("DROP TABLE posts_serving;")
        #conn.execute("DROP TABLE comments;")
        #conn.execute("DROP TABLE users;")

        # Create posts_serving if not exist.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS posts_serving ("
            # TODO: Shrink it to 24 characters.
            "post_url_hash CHAR(64) NOT NULL, "
            "post_url  TEXT(2084) NOT NULL, "
            "submission_time DATETIME, "
            "title TEXT(1024), "
            "main_image_url TEXT(2084), "
            "description TEXT(2048), "
            "user_display_name VARCHAR(100), "
            "user_email VARCHAR(255), "
            "user_photo_url TINYTEXT, "
            "user_provider_id VARCHAR(100), "
            "user_id VARCHAR(100), "
            "featured_comment TEXT(2048), "
            "featured_comment_submission_time DATETIME, "
            "featured_comment_user_display_name VARCHAR(100), "
            "featured_comment_user_email VARCHAR(255), "
            "featured_comment_user_photo_url TINYTEXT, "
            "featured_comment_user_id VARCHAR(100), "
            "PRIMARY KEY(post_url_hash) "
            ");"
        )

        # Create comments if not exist.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS comments ("
            "post_url TINYTEXT, "
            "comment TEXT(2048), "
            "submission_time DATETIME, "
            "user_id VARCHAR(100), "
            "user_display_name VARCHAR(100), "
            "user_photo_url TINYTEXT, "
            "user_email VARCHAR(255) "
            ");"
        )

        # Create users if not exist.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "user_id VARCHAR(100), "
            "user_display_name VARCHAR(100), "
            "user_email VARCHAR(255), "
            "user_photo_url TINYTEXT, "
            "user_provider_id VARCHAR(100), "
            "lastest_login_time DATETIME, "
            "sign_up_time DATETIME "
            ");"
        )

    num_posts = 0
    with db.connect() as conn:
        # Execute the query and fetch all results
        recent_posts = conn.execute(
            "SELECT count(*) as num_posts "
            "FROM posts_serving "
            "ORDER BY submission_time DESC LIMIT 10"
        ).fetchall()
        num_posts = recent_posts[0][0]

    if num_posts > 0:
        return

    stmt = sqlalchemy.text(
        "INSERT INTO posts_serving ("
        "  post_url_hash, post_url, submission_time, title, main_image_url, description, "
        "  user_display_name, user_email, user_photo_url, user_provider_id, user_id, "
        "  featured_comment, featured_comment_submission_time, "
        "  featured_comment_user_display_name, featured_comment_user_email, "
        "  featured_comment_user_photo_url, featured_comment_user_id) "
        "VALUES ("
        "  :post_url_hash, :post_url, :submission_time, :title, :main_image_url, :description, "
        "  :user_display_name, :user_email, :user_photo_url, :user_provider_id, :user_id, "
        "  :featured_comment, :featured_comment_submission_time, "
        "  :featured_comment_user_display_name, :featured_comment_user_email, "
        "  :featured_comment_user_photo_url, :featured_comment_user_id "
        ")"
    )
    try:
        time_now = datetime.datetime.utcnow()
        with db.connect() as conn:
            conn.execute(
                stmt, post_url_hash="deadbeafdeadbeaf",
                post_url="https://news.v.daum.net/v/20200816080119455", submission_time=time_now,
                title="美 입양한인 \"나를 잃어버린 부모 눈물의 나날 보내고 있을 것\"",
                main_image_url="https://img1.daumcdn.net/thumb/S1200x630/?fname=https://t1.daumcdn.net/news/202008/16/yonhap/20200816080119500cqms.jpg",
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
    except db.Error as ex:
        logger.exception(ex)
        return Response(
            status=500,
            response="Unable to successfully cast vote! Please check the "
            "application logs for more details.",
        )
