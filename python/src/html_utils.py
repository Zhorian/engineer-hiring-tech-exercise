from bs4 import BeautifulSoup

IGNORABLE_LINKS = ["#", "/"]  # Add more ignorable links if needed

def extract_links(html_content):
    """
    Extract all links (href attributes) from HTML content.
    Returns a list of URLs found in <a> tags.
    """
    links = []
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and href not in links and href != "/" and href.startswith("#") != True:
                links.append(href)
    except Exception as e:
        print(f"Error parsing HTML: {e}")
    
    return links