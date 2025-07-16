import logging
import os
from datetime import datetime

def setup_logger():
    # Create /logs directory
    logs_dir = os.path.join(os.path.dirname(__file__), '../logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Generate log file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"log_{timestamp}.txt")

    logger = logging.getLogger('my_app_logger')
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if not logger.hasHandlers():
        # File handler
        fh = logging.FileHandler(log_file, mode='a')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger

# Initialize logger at startup
logger = setup_logger()

def log(message, level='info'):
    if level.lower() == 'info':
        logger.info(message)
    elif level.lower() == 'warning':
        logger.warning(message)
    elif level.lower() == 'error':
        logger.error(message)
    elif level.lower() == 'debug':
        logger.debug(message)
    else:
        logger.info(message)
