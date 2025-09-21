from database import add_site

test_sites = [
    ("https://httpbin.org/html", "HTTPBin Test Page"),
    ("https://example.com", "Example Domain"),
    ("https://www.wikipedia.org", "Wikipedia"),
    ("https://www.github.com", "GitHub"),
]

for url, name in test_sites:
    add_site(url, name)
    print(f"Added {url} as {name}")