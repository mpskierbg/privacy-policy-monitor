from playwright.sync_api import sync_playwright # type: ignore
from bs4 import BeautifulSoup 
import logging
from log_config import setup_logger

logger = setup_logger(__name__)

def get_page_text_with_browser(url):
    """
    Fetch page content using Playwright to handle JS and cookie banners
    """
    with sync_playwright() as p:
        try:
            # Launch browser (headless=True means it runs in the background)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Navigate to page
            page.goto(url)

            # Try to handle cookie consent banners
            handle_cookie_banner(page)

            # Get the page content after JS execution
            content = page.content()

            # Close browser
            browser.close()

            # Clean and extract text
            return extract_text_from_html(content)
        
        except Exception as e:
            logger.error(f"Browser error fecthing {url}: {e}.")
            return None
        
def handle_cookie_banner(page):
    """
    Try to detect and accept common cookie cosent banners
    """
    # Common selectors for cookie accept buttons
    cookie_selectors = [
        'button:has-text("Accept")',
        'button:has-text("Agree")',
        'button:has-text("OK")',
        'button:has-text("I agree")',
        'button:has-text("Accept all")',
        'button:has-text("Consent")',
        'button:has-text("Allow")',
        '[aria-label*="Accept"]',
        '[aria-label*="agree"]',
        '.accept-cookies',
        '.cookie-accept',
        '#accept-cookies',
        '#cookie-accept',
        '#consent-accept',
        '#agree-cookies'
    ]

    for selector in cookie_selectors:
        try:
            if page.is_visible(selector):
                page.click(selector)
                page.wait_for_timeout(1000)
                logger.info("Cookie banner accepted.")
                break
        except:
            continue

def extract_text_from_html(html_content):
    """
    Extract clean text from HTML content
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted elements
    for element in soup(["script", "style", "nav", "header", "footer"]):
        element.decompose()

    # Get text and clean it
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
    cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

    return cleaned_text