import requests
from html_utils import extract_links

class Crawler:
    def get_all_user_agent_blocks(self, url):
        """
        Get the disallowed paths for all user agents (*) from robots.txt.
        Returns a list of disallowed paths (strings).
        """
        disallowed = []
        try:
            robots_url = f"{url.rstrip('/')}/robots.txt"
            response = requests.get(robots_url, timeout=10)
            if response.status_code != 200:
                return disallowed  # Empty list if no robots.txt
            
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
                        disallowed.append(path)
            
            return disallowed
        except Exception as e:
            print(f"Error fetching robots.txt: {e}")
            return disallowed

    def get_urls(self, url):
        urls = []
        response = requests.get(url)
        if response.status_code == 200:
            body = response.text
            urls = extract_links(body)

        return urls

    def run(self, url):
        print("Running crawler...")

        # check robots.txt for disallowed paths for all agents
        disallowed_paths = self.get_all_user_agent_blocks(url)
        if "/" in disallowed_paths:
            print("Crawling disallowed for all user agents; exiting.")
            return False
        
        domain = url.split('//')[-1].split('/')[0]
        baseUrls = self.get_urls(url)

        print(f"Found {len(baseUrls)} URLs on the page.")
        for baseUrl in baseUrls:
            print(f"Found URL: {baseUrl}")

        return True