import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name):
    """
    Sets up a logger with a consistent configuration.
    Call this at the top of each script.
    
    Args:
        name (str): Usually use __name__ to get the module's name
        
    Returns:
        logging.logger: A configured logger object.
    """

    """---SETUP LOGGING---"""
    # Create a 'logs' directory if it does not exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a log filename with today's date
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"monitor_{log_date}.log")

    # Create a logger specific to the module that calls this function
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Check if this logger already has handlers to avoid duplication
    if not logger.handlers:
        # Create a file handler which logs even debug messages
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024 * 5, # 5 MB
            backupCount=5 # Keep 5 backup files
        )
        file_handler.setLevel(logging.INFO)

        # Create a console handler to also output to the terminal
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger