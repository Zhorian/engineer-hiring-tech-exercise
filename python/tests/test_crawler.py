# tests/test_crawler.py

import pytest
from unittest.mock import patch, MagicMock
from src.crawler import Crawler

# -------------------------------
# Mock data
# -------------------------------
HTML_PAGE = """
<html>
    <body>
        <a href="/page1/">Page 1</a>
        <a href="/page2/">Page 2</a>
        <a href="http://example.com/page3/">Page 3</a>
        <a href="/admin/">Admin (should be skipped)</a>
    </body>
</html>
"""

def mock_requests_get(url, timeout=10):
    """Mock requests.get"""
    mock_resp = MagicMock()
    if url.endswith("/robots.txt"):
        mock_resp.status_code = 200
        mock_resp.text = "User-agent: *\nDisallow: /admin/"
    else:
        mock_resp.status_code = 200
        mock_resp.text = HTML_PAGE
    return mock_resp

def mock_extract_links(html):
    """Mock extract_links to return the hrefs in our sample HTML"""
    return ["/page1/", "/page2/", "http://example.com/page3/", "/admin/"]

# -------------------------------
# Tests
# -------------------------------
@patch("src.crawler.requests.get", side_effect=mock_requests_get)
@patch("src.crawler.extract_links", side_effect=mock_extract_links)
def test_crawler_basic(mock_links, mock_requests):
    crawler = Crawler(max_workers=2)
    success = crawler.run("http://example.com/")

    assert success is True
    # Root path should be correctly set
    assert crawler._root_path == "example.com"
    # Scanned URLs should include root page and page1/page2/page3
    for u in ["/page1/", "/page2/", "/page3/"]:
        assert any(u in url for url in crawler._scanned_urls)
    # Skipped URLs should contain /admin/
    assert any("/admin/" in url for url in crawler._skipped_urls)
    # Page records exist
    assert len(crawler._page_records) > 0
    # Each record has found_links
    for record in crawler._page_records:
        assert hasattr(record, "found_links")
        assert isinstance(record.found_links, list)

@patch("src.crawler.requests.get", side_effect=mock_requests_get)
@patch("src.crawler.extract_links", side_effect=mock_extract_links)
def test_crawler_duplicates(mock_links, mock_requests):
    crawler = Crawler(max_workers=2)
    crawler.run("http://example.com/")
    scanned_before = set(crawler._scanned_urls)
    crawler.run("http://example.com/")  # rerun
    scanned_after = set(crawler._scanned_urls)
    # No new URLs should be added
    assert scanned_before == scanned_after

@patch("src.crawler.requests.get", side_effect=mock_requests_get)
@patch("src.crawler.extract_links", side_effect=mock_extract_links)
def test_crawler_url_normalization(mock_links, mock_requests):
    crawler = Crawler(max_workers=2)
    crawler.run("example.com")  # missing scheme

    # All scanned URLs should start with http/https and end with /
    for url in crawler._scanned_urls:
        assert url.startswith("http://") or url.startswith("https://")
        assert url.endswith("/")

@patch("src.crawler.requests.get", side_effect=mock_requests_get)
@patch("src.crawler.extract_links", side_effect=mock_extract_links)
def test_crawler_robots_disallow(mock_links, mock_requests):
    crawler = Crawler(max_workers=2)
    crawler.run("http://example.com/")

    # Admin URL should be skipped
    assert any("/admin/" in url for url in crawler._skipped_urls)
    # No admin pages in scanned
    assert all("/admin/" not in url for url in crawler._scanned_urls)

@patch("src.crawler.requests.get", side_effect=mock_requests_get)
@patch("src.crawler.extract_links", side_effect=mock_extract_links)
def test_crawler_page_records(mock_links, mock_requests):
    crawler = Crawler(max_workers=2)
    crawler.run("http://example.com/")

    # Page records should contain all scanned URLs except skipped
    for record in crawler._page_records:
        for link in record.found_links:
            assert link in crawler._scanned_urls or link in crawler._skipped_urls