import logging
import os
import sys

def setup_logger(name: str, log_file: str = "app.log", level=logging.INFO) -> logging.Logger:
    """Sets up a logger with console and file handlers."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Default logger for the application
logger = setup_logger("ScreenshotSearchEngine")
