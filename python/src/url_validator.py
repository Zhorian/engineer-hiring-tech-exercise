"""Module for URL validation."""

from urllib.parse import urlparse

def validate_url(url):
    """Validate if the given string is a valid URL."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False