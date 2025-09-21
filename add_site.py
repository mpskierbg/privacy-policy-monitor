from database import add_site

def main():
    # You can add sites directly here or accept command line arguements
    sites_to_add = [
        ("https://www.example.com/privacy", "Example Company"),
        ("https://www.google.com/policies/privacy/", "Google"),
        ("https://www.verizon.com/about/privacy/", "Verizon")
        # Add more sites as needed
    ]

    for url, name in sites_to_add:
        add_site(url, name)

if __name__ == "__main__":
    main()