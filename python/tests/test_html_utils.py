import os
import pytest
from src.html_utils import extract_links


TEST_RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'resources', 'test_html_utils')

    
def load_html_file(filename):
    """Helper function to load HTML test files."""
    filepath = os.path.join(TEST_RESOURCES_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def test_extract_links_with_multiple_links():
    """Test extracting links from HTML with multiple <a> tags."""
    html_content = load_html_file('has_links.html')
    links = extract_links(html_content)
    
    assert len(links) == 2
    assert '#' not in links
    assert 'https://example.com' in links
    assert 'https://another-example.com' in links


def test_extract_links_with_no_links():
    """Test extracting links from HTML with no <a> tags."""
    html_content = load_html_file('no_links.html')
    links = extract_links(html_content)
    
    assert len(links) == 0
    assert links == []


def test_extract_links_with_only_css_links():
    """Test that CSS <link> tags are not extracted as page links."""
    html_content = load_html_file('just_css_links.html')
    links = extract_links(html_content)
    
    # Should not include CSS links from <link> tags
    assert len(links) == 0
    assert 'styles.css' not in links
    assert 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap' not in links


def test_extract_links_with_text_urls():
    """Test that URLs as plain text are not extracted."""
    html_content = load_html_file('links_as_text.html')
    links = extract_links(html_content)
    
    # Plain text URLs should not be extracted
    assert len(links) == 0


def test_extract_links_with_invalid_html():
    """Test that the function handles malformed HTML gracefully."""
    html_content = load_html_file('malformed_html.html')
    links = extract_links(html_content)
    
    # Should still extract links despite malformed HTML
    assert len(links) == 2
    assert 'http://example.com' in links
    assert 'http://test.com' in links


def test_extract_links_with_relative_urls():
    """Test that relative URLs are extracted correctly."""
    html_content = load_html_file('relative_links.html')
    links = extract_links(html_content)
    
    assert len(links) == 3
    assert '/about' in links
    assert './contact.html' in links
    assert '../other' in links


def test_extract_links_with_empty_href():
    """Test that empty href attributes are ignored."""
    html_content = load_html_file('empty_href.html')
    links = extract_links(html_content)
    
    assert len(links) == 1
    assert 'https://example.com' in links
