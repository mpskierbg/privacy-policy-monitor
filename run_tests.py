import subprocess
import sys
from log_config import setup_logger

logger = setup_logger(__name__)

def run_tests():
    """Run all test scripts"""
    tests = [
        "test_database.py",
        "test_scraping.py",
        "test_monitor.py" 
    ]

    passed = 0
    failed = 0

    for test in tests:
        logger.info(f"Running {test}...")
        result = subprocess.run([sys.executable, test], capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"{test} passed.")
            passed += 1
        else:
            logger.error(f"{test} failed.")
            logger.error(f"Error output: {result.stderr}.")
            failed += 1
    
    logger.info(f"Test results: {passed} passed, {failed} failed.")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)