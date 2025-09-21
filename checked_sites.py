from database import get_db_connection
from log_config import setup_logger

logger = setup_logger(__name__)  # __name__ will be 'checked_sites' for this file

def list_monitored_sites():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, url, site_name, last_checked FROM monitored_sites")
    sites = cursor.fetchall()
    
    if not sites:
        print("No sites found in the database.")
        return
    
    logger.info("\nMonitored Sites:")
    logger.info("-" * 50)
    for site in sites:
        id, url, name, last_checked = site
        logger.info(f"ID: {id}")
        logger.info(f"URL: {url}")
        logger.info(f"Name: {name}")
        logger.info(f"Last Checked: {last_checked}")
        logger.info("-" * 50)
    
    conn.close()

if __name__ == "__main__":
    list_monitored_sites()