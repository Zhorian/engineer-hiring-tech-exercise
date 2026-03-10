import requests
import json
from urllib.parse import urlparse, urljoin
from datetime import datetime
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import page_record
from .html_utils import extract_links
from .url_validator import is_crawlable, normalize_url

class Crawler:
    def __init__(self, max_workers=10):
        self._root_path = ""
        self._disallowed_paths = []
        self._scanned_urls = set()
        self._page_records = []
        self._skipped_urls = set()
        self._max_workers = max_workers  # updated

    def _get_all_user_agent_blocks(self, url):
        """Fetch disallowed paths from robots.txt for all user agents (*)"""
        self._disallowed_paths = []
        try:
            robots_url = urljoin(url, "/robots.txt")
            response = requests.get(robots_url, timeout=10)
            if response.status_code != 200:
                return

            content = response.text
            lines = content.splitlines()
            in_all_user_agent = False

            for line in lines:
                line = line.strip()
                if line.lower().startswith("user-agent:"):
                    user_agent = line.split(":", 1)[1].strip()
                    in_all_user_agent = user_agent == "*"
                elif in_all_user_agent and line.lower().startswith("disallow:"):
                    path = line.split(":", 1)[1].strip()
                    if path:
                        self._disallowed_paths.append(f"http://{self._root_path}{path}")
                        self._disallowed_paths.append(f"https://{self._root_path}{path}")

        except Exception as e:
            print(f"Error fetching robots.txt: {e}")
            self._disallowed_paths = [
                f"http://{self._root_path}/",
                f"https://{self._root_path}/",
            ]

    def _crawl_url(self, url):
        """Crawl a single URL and return found links"""
        url = normalize_url(url)
        if not url.endswith("/"):
            url += "/"

        if url in self._scanned_urls or not is_crawlable(url, self._root_path, self._disallowed_paths):
            self._skipped_urls.add(url)
            return []

        print(f"Scanning {url}")
        self._scanned_urls.add(url)
        record = page_record.PageRecord()
        record.page = url
        found_urls = []

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                body = response.text
                found_urls = extract_links(body)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            self._skipped_urls.add(url)
            return []

        # Normalize relative URLs
        normalized_urls = []
        for u in found_urls:
            if u.startswith("/"):
                u = f"http://{self._root_path}{u}"
            normalized_urls.append(u)

        record.found_links = normalized_urls
        if normalized_urls:
            self._page_records.append(record)

        return normalized_urls


    def _dump_to_json(self, name, obj):
        with open(f"{name}.json", "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)

    def run(self, url):
        print("Running crawler...")

        parsed = urlparse(url)
        self._root_path = parsed.netloc
        print(f"Using root path {self._root_path}")

        # Get robots.txt disallowed paths
        self._get_all_user_agent_blocks(url)
        if f"{self._root_path}/" in self._disallowed_paths:
            print("Crawling disallowed for all user agents; exiting.")
            return False

        to_crawl = deque([normalize_url(url)])
        started = datetime.now()
        print(f"Starting scanning at {started}")

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {}

            while to_crawl or futures:
                # Submit new URLs to executor
                while to_crawl and len(futures) < self._max_workers:
                    next_url = to_crawl.popleft()
                    future = executor.submit(self._crawl_url, next_url)
                    futures[future] = next_url

                # Process completed futures
                done, _ = as_completed(futures), []
                for future in done:
                    found_urls = future.result()
                    for u in found_urls:
                        if u not in self._scanned_urls:
                            to_crawl.append(u)
                    del futures[future]
                    break  # process one at a time to refill executor

        finished = datetime.now()
        print(f"Finished scanning at {finished} took {finished - started}")

        # Save results
        pages_dicts = [vars(page) for page in self._page_records]
        pages_dicts.sort(key=lambda x: x["page"])
        self._dump_to_json("data", pages_dicts)

        skipped_list = sorted(self._skipped_urls)
        self._dump_to_json("skipped", skipped_list)

        scanned_list = sorted(self._scanned_urls)
        self._dump_to_json("scanned", scanned_list)

        return True