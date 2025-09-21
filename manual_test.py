from browser_handler import get_page_text_with_browser

# Test with sites known to have cookie banners
test_sites = [
    "https://www.bbc.com",
    "https://www.theguardian.com",
    "https://www.cnn.com"
]

for site in test_sites:
    print(f"Testing {site}...")
    try:
        text = get_page_text_with_browser(site)
        print(f"Success: Got {len(text)} characters")
    except Exception as e:
        print(f"Error: {e}")