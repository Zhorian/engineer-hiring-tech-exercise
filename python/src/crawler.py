import requests
import page_record
import json
from html_utils import extract_links
from urllib.parse import urlparse
from datetime import datetime

class Crawler:
    _domain = ""
    _disallowed_paths = []
    _scanned_urls = []
    _page_records = []

    def get_all_user_agent_blocks(self, url):
        """
        Get the disallowed paths for all user agents (*) from robots.txt.
        Returns a list of disallowed paths (strings).
        """
        self._disallowed_paths = []
        try:
            robots_url = f"{url.rstrip('/')}/robots.txt"
            response = requests.get(robots_url, timeout=10)
            if response.status_code != 200:
                return # Empty list if no robots.txt
            
            content = response.text
            lines = content.split('\n')
            in_all_user_agent = False
            
            for line in lines:
                line = line.strip()
                if line.lower().startswith('user-agent:'):
                    user_agent = line.split(':', 1)[1].strip()
                    if user_agent == '*':
                        in_all_user_agent = True
                    else:
                        in_all_user_agent = False
                elif in_all_user_agent and line.lower().startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        self._disallowed_paths.append(f"{self._domain}{path}")
        except Exception as e:
            print(f"Error fetching robots.txt: {e}")
            self._disallowed_paths = [f"{self._domain}/"]

    def get_urls(self, url):
        url = url if url.endswith("/") else f"{url}/"

        if not url.startswith(self._domain):
            # print(f"DOMAIN: Url '{url}' not in domain, I will crawl no further!")
            return
        
        if(url in self._scanned_urls):
            # print(f"SCANNED: Already scanned url '{url}, I'm not doing it again")
            return
        
        if any(url.startswith(path) for path in self._disallowed_paths):
            # print(f"FORBIDDEN: Url {url} is disallowed, I shall not pass!")
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
                found_urls[i] = f"{self._domain}{found_urls[i]}"

            record.found_links = found_urls

        if len(record.found_links) > 0:
            self._page_records.append(record)
        
        self._scanned_urls.append(url)

        for found_url in found_urls:
            self.get_urls(found_url)

    def run(self, url):
        print("Running crawler...")

        parsed = urlparse(url)
        self._domain = f"{parsed.scheme}://{parsed.netloc}"
        print(f"Using domain {self._domain}")

        # check robots.txt for disallowed paths for all agents
        self.get_all_user_agent_blocks(url)
        if f"{self._domain}/" in self._disallowed_paths:
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

        return True