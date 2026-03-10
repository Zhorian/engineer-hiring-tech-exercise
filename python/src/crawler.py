import requests
import page_record
import json
from html_utils import extract_links
from urllib.parse import urlparse, urljoin
from datetime import datetime
from url_validator import is_crawlable, normalize_url

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

    def get_urls(self, url):
        url = normalize_url(url)
        url = url if url.endswith("/") else f"{url}/"

        if not is_crawlable(url, self._root_path, self._disallowed_paths):
            self._skipped_urls.add(url)
            return
        
        if(url in self._scanned_urls):
            # print(f"SCANNED: Already scanned url '{url}, I'm not doing it again")
            return
        
        print(f"Scanning {url}")
        record = page_record.PageRecord()
        record.page = url
        
        found_urls = []

        response = requests.get(url)
        if response.status_code == 200:
            body = response.text
            found_urls = extract_links(body)

        print(f"Found {len(found_urls)} URLs on the page {url}.")

        for i in range(0, len(found_urls)):
            if(found_urls[i][0] == "/"):
                found_urls[i] = f"{self._root_path}{found_urls[i]}"

            record.found_links = found_urls

        if len(record.found_links) > 0:
            self._page_records.append(record)
        
        self._scanned_urls.add(url)

        for found_url in found_urls:
            self.get_urls(found_url)

    def run(self, url):
        print("Running crawler...")

        parsed = urlparse(url)
        self._root_path = f"{parsed.netloc}"
        print(f"Using root path {self._root_path}")

        # check robots.txt for disallowed paths for all agents
        self._get_all_user_agent_blocks(url)
        if f"{self._root_path}/" in self._disallowed_paths:
            print("Crawling disallowed for all user agents; exiting.")
            return False
    
        started = datetime.now()
        print(f"Starting scanning at {started}")
        self.get_urls(url)
        finished = datetime.now()
        print(f"Finished scanning at {finished} took {finished - started}")

        pages_dicts = [vars(page) for page in self._page_records]
        pages_dicts.sort(key=lambda x: x["page"])

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(pages_dicts, f, ensure_ascii=False, indent=4)

        skipped_list = sorted(self._skipped_urls)
        with open("skipped.json", "w", encoding="utf-8") as f:
            json.dump(skipped_list, f, ensure_ascii=False, indent=4)

        return True