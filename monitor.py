from database import get_db_connection
from database import mark_site_as_requires_browser
import requests
from bs4 import BeautifulSoup
import difflib
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config # type: ignore
from log_config import setup_logger
from browser_handler import get_page_text_with_browser

# Need to figure out how to check if 'privacy_policies.db exists and if not to create it,
# I only ran it in a seperate script to create it for now.
"""conn = sqlite3.connect('privacy_polices.db')
c = conn.cursor()

# Create a table to storethe monitored sites and their latest content
c.execute('''
    CREATE TABLE IF NOT EXISTS monitored_sites (
          id INTEGER PRIMARY KEY,
          url TEXT UNIQUE NOT NULL,
          site_name TEXT,
          last_checked TEXT,
          last_content TEXT
    )
''')

conn.commit()
conn.close()
print("Database initialized.")"""
# Set up centralized logger
logger = setup_logger(__name__) # __name__ will be 'monitor for this file

def get_page_text(url, use_browser=False):
    """Function to fetch and clean text from a URL"""
    if use_browser:
        return get_page_text_with_browser(url)
    else:
        try:
            logger.debug(f"Fetching URL: {url}")  # Debug level for very detailed info
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raises an error for bad status codes
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove scripts, styles, and extra whitespace
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

            return cleaned_text
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}.")
            return None

def find_diffs(old_text, new_text):
    """Function to compare new text from get_page_text with old text"""
    if old_text == new_text:
        return None
    
    # This creates a unified diff output
    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile='Previous Version',
        tofile='Current Version',
        n=3 # Number of context lines around changes
    )
    return ''.join(diff)

def get_all_sites():
    """ Function to get all monitored sites from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, site_name, last_content FROM monitored_sites")
    sites = cursor.fetchall()
    conn.close()
    return sites

def update_site_content(site_id, new_content):
    """Function to update a site's content and timestamp in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    current_time = datetime.utcnow().isoformat()
    cursor.execute(
        "UPDATE monitored_sites SET last_content = ?, last_checked = ? WHERE id = ?",
        (new_content, current_time, site_id)
    )
    conn.commit()
    conn.close()

def send_alert(url, site_name, diff_output):
    """Function to send email alert"""
    msg = MIMEMultipart()
    msg['Subject'] = f'ALERT: Privacy Policy Changed for {site_name or url}'
    msg['From'] = config.EMAIL_ADDRESS
    msg['To'] = config.EMAIL_ADDRESS

    body = f"""
    Changes detected for the privacy policy at: {url}
    Site Name: {site_name}

    Diff Output:
    {diff_output}
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            server.send_message(msg)
        logger.info(f"Alert email sent for {url}.")
    except Exception as e:
        logger.error(f"Failed to send email for {url}.")

def check_all_sites():
    """Main function to check all sites"""
    sites = get_all_sites()
    logger.info(f"Found {len(sites)} sites to monitor")

    for site in sites:
        site_id, url, site_name, old_content, requires_browser = site  # Updated to get the new column
        logger.info(f"Checking {url}...")

        # Use browser directly if we know its required already
        if requires_browser:
            current_text = get_page_text(url, use_browser=True)
        else:
            # Try with requests first, then fall back to browser if needed
            current_text = get_page_text(url, use_browser=False)
            if should_use_browser(current_text, url):
                current_text = get_page_text(url, use_browser=True)
                mark_site_as_requires_browser(site_id)

        # Try with requests first (fast), fall back to browser if needed
        current_text = None
        use_browser = False
        
        # First attempt: try regular requests
        current_text = get_page_text(url, use_browser=False)

        if should_use_browser(current_text, url):
            logger.info(f"Falling back to browser for {url}.")
            current_text = get_page_text(url, use_browser=True)
            use_browser = True

        if current_text is None:
            logger.error(f"Failed to fetch content for {url} even with browser fallback.")
            continue # Skip to next site if we cant fetch this one

        if use_browser:
            # Could add logic here to mark this site as requiring browser in the future
            logger.info(f"Successfully used brownser for {url}. Consider adding to browser list.")


        # If we have no previous content, just store the current content
        if old_content is None:
            logger.info(f"First run for {url}. Storing initial version.")
            update_site_content(site_id, current_text)
            continue

        # Check for differences
        differences = find_diffs(old_content, current_text)
        if differences:
            logger.warning(f"CHANGES DETECTED for {url}!")
            send_alert(url, site_name, differences)
            update_site_content(site_id, old_content)
        else:
            logger.info(f"No changes for {url}.")
            # Update the last_checked timestamp, even if no changes
            update_site_content(site_id, old_content)    

def should_use_browser(content, url): 
    """
    Determine if we should use browser automation for this site.
    Returns True if content suggests JS-rendered page or cookie wall"""
    if content is None:
        logger.debug(f"Content is None for {url}, will try browser.")
        return True

    # Check if content is suspiciously short (suggesting a cookie wall)
    if len(content) < 1000: # Privacy policies are typically long
        logger.debug(f"Content too short ({len(content)} chars) for {url}, will try browser.") 
        return True
    
    # Check for common cookie banner indicators
    cookie_indicators = [
        "cookie", "consent", "gdpr", "privacy settings", 
        "accept all", "agree", "manage cookies"
        ]

    content_lower = content.lower()
    for indicator in cookie_indicators:
        if indicator in content_lower:
            logger.debug(f"Found cookie indicator '{indicator}' in {url}, will try browser.")
            return True

    # Check for JS framework indicators
    js_indicators = [
        "react", "vue", "angular", "window.__", "window.gon",
        "script", "function(", "var ", "const ", "let "
    ]    

    for indicator in js_indicators:
        if indicator in content_lower:
            logger.debug(f"Found JS indicator '{indicator}' in {url}, will try browser.")
            return True
    
    return False
       
# --- Main Execution for Testing ---
if __name__ == "__main__":
    check_all_sites()

    """ 1. Do better scrap
        2. Set up scheduling"""