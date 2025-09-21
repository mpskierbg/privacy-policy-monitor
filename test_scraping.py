from browser_handler import get_page_text_with_browser, extract_text_from_html
from monitor import get_page_text, should_use_browser
from log_config import setup_logger

logger = setup_logger(__name__)

def test_scraping_functions():
    """Test web scraping functions"""
    logger.info("Starting scraping tests...")

    # Test urls
    simple_url = "https://httpbin.org/html"
    # AVOID TESTING ON PRODUCTION SITES DURING DEVELOPMENT

    # Test 1: Basic requests-based scraping
    try:
        text = get_page_text(simple_url, use_browser=False)
        if text and len(text > 0):
            logger.info("Basic requests scraping works.")
        else:
            logger.error("Basic requests scraping returned no content.")
            return False
    except Exception as e:
        logger.error(f"Basic requests scraping failed: {e}.")
        return False
    
    # Test 2: Browser-based scraping
    try:
        text = get_page_text_with_browser(simple_url)
        if text and len(text) > 0:
            logger.info("Browser-based scraping works.")
        else:
            logger.error("Browser-based scraping returned no content.")
            return False
    except Exception as e:
        logger.error(f"Browser-based scraping failed: {e}.")
        return False
    
    # Test 3: Test browser detection login
    test_cases = [
        (None, True, "None content"),
        ("Short", True, "Short content"),
        ("This is a long text that should not trigger browser fallback" * 20, False, "Long content"),
        ("This text contains cookie consent language", True, "Content with cookie keywords"),
    ]

    for content, expected, description in test_cases:
        result = should_use_browser(content, "http://example.com")
        if result == expected:
            logger.info(f"Browser-based detection correct for: {description}.")
        else:
            logger.error(f"Browser-based detection wrong for: {description}.")
            return False

    logger.info("All scraping tests passed.")
    return True

if __name__ == "__main__":
    test_scraping_functions()   