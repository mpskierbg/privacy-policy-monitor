from database import get_db_connection, check_add_column, add_site, mark_site_as_requires_browser
from log_config import setup_logger

logger = setup_logger(__name__)

def test_database_operations():
    """Test all database operations"""
    logger.info("Starting database tests...")

    # Test 1: Add a test site
    test_url = "https://httpbin.org/html"
    test_name = "Test Site"

    try:
        add_site(test_url, test_name)
        logger.info("Successfully added test site")
    except Exception as e:
        logger.error("Failed to add test site.")
        return False
    
    # Test 2: Add a new column to the schema
    try:
        success = check_add_column("test_column", "TEXT DEFAULT 'test_value'")
        if success:
            logger.info("Successfully added test column")
        else:
            logger.info("Test column already exists (this is okay).")
    except Exception as e:
        logger.error("Failed to add test column.")
        return False
    
    # Test 3: Test marking a site as requiring browser
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM monitored_sites WHERE url = ?", (test_url,))
        site_id = cursor.fetchone()[0]
        conn.close()

        mark_site_as_requires_browser(site_id)
        logger.info("Successfully marked site as requiring browser.")
    except Exception as e:
        logger.error("Failed to mark site as requiring browser.")
        return False
    
    logger.info("All database tests passed.")
    return True

if __name__ == "__main__":
    test_database_operations()