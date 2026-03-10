"""Module for URL validation."""

from urllib.parse import urlparse
import os

# Allowed webpage extensions
ALLOWED_EXTENSIONS = {"", ".html", ".htm", ".php", ".asp", ".aspx"}


def normalize_url(url: str) -> str:
    """Ensure URL has a scheme for parsing."""
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    return url


def validate_url(url: str) -> bool:
    """Validate if the given string is a valid HTTP/HTTPS URL."""
    try:
        parsed = urlparse(url)
        return parsed.scheme.lower() in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def is_crawlable(url: str, root_path: str, disallowed_paths: list[str]) -> bool:
    """
    Determine if a URL is crawlable.

    Rules:
    1. Must match exact root domain.
    2. Must not be in disallowed paths.
    3. Must have an allowed webpage extension.
    """
    url = normalize_url(url)
    parsed = urlparse(url)

    # Exact root domain match
    if parsed.netloc.lower() != root_path.lower():
        return False

    # Path for checks
    path_lower = parsed.path.lower()

    # Check disallowed paths (prefix match, case-insensitive)
    for p in disallowed_paths:
        p_path = urlparse(normalize_url(p)).path.lower().rstrip("/")
        if path_lower == p_path or path_lower.startswith(p_path + "/") or path_lower.startswith(p_path + "."):
            # Exact match, subpath, or file starting with disallowed prefix
            return False

    # Check allowed extensions (ignore query strings)
    path_no_query = parsed.path.split("?", 1)[0].lower()
    ext = os.path.splitext(path_no_query)[1]
    if ext and ext not in ALLOWED_EXTENSIONS:
        return False

    return True