from src.crawler import run, get_all_user_agent_blocks
import pytest
from unittest.mock import patch
import os

TEST_RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'resources', 'test_crawler')

def load_test_file(filename):
    with open(os.path.join(TEST_RESOURCES_DIR, filename), 'r') as f:
        return f.read()

def test_run(capsys):
    # ensure run proceeds when no root disallow
    with patch('src.crawler.get_all_user_agent_blocks') as mock_blocks:
        mock_blocks.return_value = []
        with patch('src.crawler.requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 404
            result = run("http://example.com")
            assert result is True
            captured = capsys.readouterr()
            assert "Running crawler..." in captured.out


def test_run_disallowed_all(capsys):
    with patch('src.crawler.get_all_user_agent_blocks') as mock_blocks:
        mock_blocks.return_value = ['/']
        result = run("http://example.com")
        assert result is False
        captured = capsys.readouterr()
        assert "Crawling disallowed for all user agents" in captured.out

def test_get_all_user_agent_blocks_with_disallow_admin():
    with patch('src.crawler.requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = load_test_file('robots_disallow_admin.txt')
        result = get_all_user_agent_blocks("http://example.com")
        assert result == ["/admin"]

def test_get_all_user_agent_blocks_with_disallow_all():
    with patch('src.crawler.requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = load_test_file('robots_disallow_all.txt')
        result = get_all_user_agent_blocks("http://example.com")
        assert result == ["/"]

def test_get_all_user_agent_blocks_with_googlebot():
    with patch('src.crawler.requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = load_test_file('robots_with_googlebot.txt')
        result = get_all_user_agent_blocks("http://example.com")
        assert result == ["/private", "/admin"]

def test_get_all_user_agent_blocks_no_robots():
    with patch('src.crawler.requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 404
        result = get_all_user_agent_blocks("http://example.com")
        assert result == []