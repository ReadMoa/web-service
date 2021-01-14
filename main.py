"""ReadMoa web API server.

Provide handlers for APIs, static images/HTMLs.
"""
import logging
import os
from urllib.parse import urlparse, urljoin

# For parsing a webpage.
from bs4 import BeautifulSoup
# pylint: disable=line-too-long
from flask import Flask, jsonify, make_response, render_template, request, Response, send_from_directory
from flask_cors import CORS

# For crawling a webpage.
import requests
from util.post import Post
from util.post_db import PostDB

# Max post index to return in /api/list_posts
MAX_POSTS_TO_START = 1000
DATABASE_MODE = "prod"

app = Flask(__name__, template_folder='webapp/build')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
logger = logging.getLogger()

post_db = PostDB(DATABASE_MODE)

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

@app.route("/favicon.ico", methods=["GET"])
def resource_favicon():
    """Returns the favicon file.

    Returns:
      favicon.ico.
    """
    return send_from_directory("static", "favicon.ico")

@app.route('/images/<path:path>')
def serve_image(path):
    """Returns a image file.

    Args:
      path: A path to image file.

    Returns:
      An image file from /static/images directory.
    """
    return send_from_directory('static/images', path)

@app.route('/static/<path>/<filename>', methods=["GET"])
def serve_static(path, filename):
    """Returns a static file.

    Args:
      path: A path to a static file.

    Returns:
      An image file from /static/ directory.
    """
    return send_from_directory(os.path.join("webapp/build/static", path), filename)

@app.route('/manifest.json')
def manifest_json():
    """Returns manifest.json file.

    Returns:
      manifest.json
    """
    return send_from_directory('webapp/build', 'manifest.json')

@app.route("/p/<path:path>", methods=["GET"])
def view_page(path):
    """Renders a view_post page (/p/)

    Renders a view_post.html from a post with the input post key.

    Args:
      path: 96bit (24 hexadecimal digits) post key.
    """
    post = post_db.lookup(path)

    if not post:
        return Response(
                status=404,
                response="The post is not available.")

    return render_template("index.html", post=post)

@app.route("/write_post", methods=["GET"])
def write_post():
    """Renders write_post page.

    Renders write_post page.
    """
    # Creates a fake Post object for populating meta data for index.html.
    post = Post(
            post_url="", author="", title="리드모아 - 읽을거리 추가하기",
            description="다른 사람들과 함께 읽을거리를 추가해주세요.",
            published_date=None)

    return render_template("index.html", post=post)

@app.route("/", methods=["GET"])
def main_page():
    """Renders the root(/) page.

    Renders the root page.
    """
    # Creates a fake Post object for populating meta data for index.html.
    post = Post(
            post_url="", author="", title="리드모아 - 다양한 읽을거리, 더 읽을 거리",
            description="읽을거리가 필요하신가요? 리드모아에서 시간을 보내세요. 읽을거리가 여러분을 찾아갑니다.",
            published_date=None)

    return render_template("index.html", post=post)

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

    count = 10
    if request.args.get("count") is not None:
        count = int(request.args.get("count"))

    recent_posts = post_db.scan(start_idx=start_idx, count=count)

    posts = []
    for post in recent_posts:
        posts.append({
            "post_url_hash": post.post_url_hash,
            "post_url": post.post_url,
            "title": post.title,
            "submission_time": post.submission_time,
            "main_image_url": post.main_image_url,
            "description": post.description})
    response = make_response(jsonify(posts=posts))
    response.cache_control.max_age = 30
    return response

# JSON data format for request.
# {
#   "url": "..."
#   "comment": "..."
#   "idtoken": "..."
# }
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
    # Can't extract the published date yet.
    published_date = 0
    author = ""

    post = Post(
            post_url=url, title=title, main_image_url=main_image,
            description=description, user_display_name="모아인",
            user_provider_id="Moain", user_id="Moain",
            published_date=published_date, author=author)
    post_db.insert(post)

    return_post = {
            "post_url_hash": post.post_url_hash,
            "post_url": post.post_url,
            "title": post.title,
            "submission_time": post.submission_time,
            "main_image_url": post.main_image_url,
            "description": post.description}
    response = make_response(jsonify(post=return_post))
    response.cache_control.max_age = 30
    return response

@app.route('/sitemap.xml')
def sitemap_xml():
    """Returns sitemap.xml data.

    The sitemap is in a format below:
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>http://www.example.com/foo.html</loc>
            <lastmod>2018-06-04</lastmod>
        </url>
    </urlset>

    Request params:
      N/A

    Returns:
      sitemap.xml data.
    """
    recent_posts = post_db.scan(count=1000)
    modified_posts = []
    for post in recent_posts:
        modified_posts.append({
            "post_url": post.post_url,
            "submission_date": post.submission_time.date()})

    template = render_template('sitemap.xml', posts=modified_posts)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
