from monitor import check_all_sites, get_all_sites
from database import add_site
from log_config import setup_logger

logger = setup_logger(__name__)

def test_monitoring_flow():
    """Test the complete monitoring flow"""
    logger.info("Starting monitoring flow test...")

    # Add a test site
    test_url = "https://httpbin.org/html"
    test_name = "Monitoring Test Site"

    try:
        add_site(test_url, test_name)
        logger.info("Added test site for monitoring.")
    except Exception as e:
        logger.error("Failed to add test site.")
        return False

    # Run the monitoring
    try:
        check_all_sites()
        logger.info("Monitoring completed successfully.")
    except Exception as e:
        logger.error(f"Monitoring failed {e}.")
        return False
    
    # Verify the site was checked
    try:
        sites = get_all_sites()
        test_site = None
        for site in sites:
            if site[1] == test_url:
                test_site = site
                break
        if test_site and test_site[3]: 
            logger.info("Test site was properly checked and updated.")
        else:
            logger.info("Test site was not properly checked.")
            return False
    except Exception as e:
        logger.error(f"Failed to verify monitoring results: {e}.")
        return False
    
    logger.info("All monitoring tests passed.")
    return True

if __name__ == "__main__":
    test_monitoring_flow()