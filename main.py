"""ReadMoa web API server.

Provide handlers for APIs, static images/HTMLs.
"""
import datetime
import logging
import os
from urllib.parse import urlparse, urljoin

# For parsing a webpage.
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request, Response, send_from_directory
from flask_cors import CORS

# For crawling a webpage.
import requests
import sqlalchemy
from util import database
from util import url as url_util

# Max post index to return in /api/list_posts
MAX_POSTS_TO_START = 1000
DATABASE_MODE = "prod"

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
logger = logging.getLogger()


db = database.init_connection_engine()

@app.before_first_request
def google_service_init():
    """A function to be run before the first request to this instance of the application.
    """
    # no-op
    return

@app.route("/privacy", methods=["GET"])
def page_privacy():
    """Returns privacy document.

    Returns:
      privacy.html.
    """
    privacy_admin = {}
    privacy_admin["name"] = os.environ["PRIVACY_ADMIN_NAME"]
    privacy_admin["email"] = os.environ["PRIVACY_ADMIN_EMAIL"]
    privacy_admin["phone"] = os.environ["PRIVACY_ADMIN_PHONE"]
    return render_template(
        "privacy.html", privacy_admin=privacy_admin)

@app.route("/terms", methods=["GET"])
def page_terms():
    """Returns terms document.

    Returns:
      terms.html.
    """
    return render_template("terms.html")

# TODO: Use a more efficient way to serve static files e.g. nginx.
@app.route("/favicon.ico", methods=["GET"])
def resource_favicon():
    """Returns the favicon file.

    Returns:
      favicon.ico.
    """
    return send_from_directory("static", "favicon.ico")

# TODO: Use a more efficient way to serve static files e.g. nginx.
@app.route('/images/<path:path>')
def serve_image(path):
    """Returns a image file.

    Args:
      path: A path to image file.

    Returns:
      An image file from /static/images directory.
    """
    return send_from_directory('static/images', path)

# TODO: Move this (page view) logic to React from Flask template rendering.
@app.route("/p/<path:path>", methods=["GET"])
def view_page(path):
    """Renders a view_post page (/p/)

    Renders a view_post.html from a post with the input post key.

    Args:
      path: 96bit (24 hexadecimal digits) post key.
    """
    post = {}
    with db.connect() as conn:
        # Execute the query and fetch all results
        returned_posts = conn.execute("""
            SELECT post_url_hash, post_url, title, submission_time, main_image_url, description, 
                   user_display_name, user_email, user_photo_url, user_id, user_provider_id 
            FROM {mode}_posts_serving 
            where post_url_hash = '{key}'
            """.format(mode=DATABASE_MODE, key=path)
        ).fetchall()
        # Convert the results into a list of dicts representing votes
        if len(returned_posts) <= 0:
            # 404
            return Response(
                status=404,
                response="The post is not available.",
            )

        row = returned_posts[0]
        post = {
                "post_url_hash": row[0],
                "post_url": row[1],
                "title": row[2],
                "submission_time": row[3],
                "main_image_url": row[4],
                "description": row[5]}

    return render_template(
        "view_post.html", post=post)

# Returns a full URL from og:url.
def get_full_url(parent_url, og_url):
    """Generates a full URL from a relative URL.

    Args:
      parent_url: The parent document's URL (assume it's a full URL).
      or_url: A URL extracted from OpenGraph metadata.

    Returns:
      A full URL string.
    """
    full_url = og_url.strip()
    if full_url.startswith("/"):
        p_url = urlparse(parent_url)
        full_url = "{scheme}://{host}{rest}".format(
            scheme=p_url.scheme, host=p_url.netloc, rest=full_url)
    elif not full_url.startswith("http"):
        # A relative URL not under the root('/') directory.
        full_url = urljoin(parent_url, full_url)

    return full_url

@app.route('/api/list_posts', methods=["GET"])
def api_list_posts():
    """Returns a list of recent posts.

    Request params
      start: the start index of recent posts (ordered by submission time).
      count: number of posts to return.
    """
    # pylint: disable=fixme
    # TODO: Can we change 'start' as an absolute position e.g. timestamp
    #       to make the result consistent even when there is a new item
    #       to posts_serving db.
    start_idx = 0
    if request.args.get("start") is not None:
        start_idx = int(request.args.get("start"))
        if start_idx < 0 or start_idx > MAX_POSTS_TO_START:
            start_idx = 0

    count = 10
    if request.args.get("count") is not None:
        count = int(request.args.get("count"))
        if count < 0 or count > MAX_POSTS_TO_START:
            count = 10

    posts = []
    with db.connect() as conn:
        # Execute the query and fetch all results
        recent_posts = conn.execute("""
            SELECT post_url_hash, post_url, title, submission_time, main_image_url, description, 
                   user_display_name, user_email, user_photo_url, user_id, user_provider_id 
            FROM {mode}_posts_serving 
            ORDER BY submission_time DESC LIMIT {limit:d}
            """.format(mode=DATABASE_MODE, limit=start_idx + count)
        ).fetchall()
        # Convert the results into a list of dicts representing votes
        if len(recent_posts) < start_idx:
            return jsonify(posts=[])

        for row in recent_posts[start_idx:]:
            posts.append({
                "post_url_hash": row[0],
                "post_url": row[1],
                "title": row[2],
                "submission_time": row[3],
                "main_image_url": row[4],
                "description": row[5]})
    return jsonify(posts=posts)

# JSON data format for request.
# {
#   "url": "..."
#   "comment": "..."
#   "idtoken": "..."
# }
# TODO: Refactor the duplicate code with add_post_submit().
# TODO: Didn't test this function.
@app.route('/api/add_post', methods=["POST"])
def api_add_post():
    """Flask handler for /api/add_post request.

    Args:
      N/A

    Returns:
      Echos the input JSON object.
    """
    post = request.json

    logger.warning('SEE HERE')
    logger.warning('add post=%s', request.get_json())

    url = post["url"]
    _comment = post["comment"]

    title = ''
    main_image = ''
    description = ''

    # Crawl and parse a webpage.
    source_code = requests.get(url).text
    soup = BeautifulSoup(source_code, 'html.parser')
    for each_text in soup.findAll('meta'):
        if each_text.get('property') == 'og:title':
            title = each_text.get('content')
        if each_text.get('property') == 'og:image':
            main_image = each_text.get('content')
        if each_text.get('property') == 'og:url':
            og_url = each_text.get('content')
            full_url = get_full_url(url, og_url)
            if full_url:
                url = full_url
                logger.info('New URL from og:url: %s', url)
            else:
                logger.warning('Failed to generate a full URL from %s', og_url)
                return Response(
                    status=500,
                    response="INSERT operation failed.",
                )
        if each_text.get('property') == 'og:description':
            description = each_text.get('content')

    url_hash = url_util.url_to_hashkey(url)
    time_cast = datetime.datetime.utcnow()

    userid = ''

    stmt = sqlalchemy.text("""
        INSERT INTO {mode}_posts_serving 
          (post_url_hash, post_url, submission_time, user_id, 
           title, main_image_url, description) 
         VALUES 
          (:url_hash, :url, :time_cast, :userid, 
           :title, :main_image, :description)
        """.format(mode=DATABASE_MODE)
    )

    logger.warning(stmt)

    try:
        with db.connect() as conn:
            conn.execute(
                    stmt, url_hash=url_hash, url=url,
                    time_cast=time_cast, userid=userid,
                    title=title, main_image=main_image,
                    description=description)
    except db.Error as ex:
        logger.exception(ex)
        return Response(
            status=500,
            response="INSERT operation failed.",
        )

    return jsonify(post=post)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
