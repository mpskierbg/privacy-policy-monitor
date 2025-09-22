from urllib.parse import urljoin, urlparse
from browser_handler import get_page_text_with_browser
from bs4 import BeautifulSoup
import re
from log_config import setup_logger
from playwright.sync_api import sync_playwright # type: ignore

logger = setup_logger(__name__)

def discover_privacy_links(main_url):
    """
    Discover all privacy-related links on a main privacy page
    """
    logger.info(f"Discovering privacy links on {main_url}.")

    # Get page content
    html_content = get_page_html(main_url)
    if not html_content:
        return[]
    
    soup = BeautifulSoup(html_content, 'html.parser')

    # Common patterns for privacy-related links
    privacy_patterns = [
        r'privacy',
        r'notice',
        r'policy',
        r'ccpa',
        r'gdpr',
        r'california',
        r'opt.?out',
        r'do not sell',
        r'your privacy choices',
        r'data rights',
        r'transparency'
    ]

    discovery_links = set()

    # Look for links in common locations
    selectors_to_check = [
        'a[href]',
        'nav a[href]',
        '.privacy-links a[href]',
        '.footer a[href]',
        '#privacy a[href]',
        '[data-component="privacy"] a[href]'
    ]

    for selector in selectors_to_check:
        links = soup.select(selector)
        for link in links:
            href = link.get('href','')
            text = link.get_text().lower()

            # Check if this looks like a privacy-related link
            if is_privacy_link(href, text, privacy_patterns):
                absolute_url = make_absolute_url(main_url, href)
                if absolute_url:
                    discovery_links.add((absolute_url, text))

    logger.info(f"Found {len(discovery_links)} privacy-related links")
    return list(discovery_links)

def is_privacy_link(href, text, patterns):
    """Determine if a link is likey privacy-related"""
    href_lower = href.lower()
    text_lower = text.lower()

    # Check against our patterns
    for pattern in patterns:
        if (re.search(pattern, href_lower) or re.search(pattern, text_lower)):
            return True
        
    # Additional checks
    if '/privacy' in href_lower:
        return True
    
    if any(term in text_lower for term in ['privacy', 'policy', 'notice', 'ccpa', 'gdpr']):
        return True
    
    return False

def make_absolute_url(base_url, relative_url):
    """Convert relative URLs to absolute URLs"""
    if relative_url.startswith(('http://', 'https://')):
        return relative_url
    try:
        return urljoin(base_url, relative_url)
    except:
        logger.warning(f"Could not make absolute URL from {base_url} and {relative_url}.")
        return None
    
def get_page_html(url):
    """Get HTML content of a page (using browser for JS rendering)"""
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
            return content
        except Exception as e:
            logger.error(f"Error getting HTML from {url}: {e}.")
            return None