"""A util module for handling URLs.

  Typical usage example:

  url = "https://example.com/"
  hash_64bit_key = url_to_haskey(url)
"""
import hashlib

def url_to_hashkey(url):
    """Generate a 64 bit hash key from a URL string.

    Args:
      url: A URL string.

    Returns:
      A 64 bit hash key.
    """
    return hashlib.sha512(url.encode()).hexdigest()[0:64]