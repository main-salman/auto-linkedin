"""
Auto LinkedIn - Python application for LinkedIn automation
"""

__version__ = "0.1.0"
__author__ = "Auto LinkedIn"
__description__ = "Python application for LinkedIn automation"

# Import key modules
from .version import VERSION

# Initialize logging
import logging
import os
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = os.path.expanduser("~/.auto_linkedin")
os.makedirs(logs_dir, exist_ok=True)

# Setup logging
log_format = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to stdout
        logging.FileHandler(os.path.join(logs_dir, "auto_linkedin.log"))  # Log to file
    ]
)

# Set specific package loggers
logger = logging.getLogger('auto_linkedin')
logger.setLevel(logging.INFO)

# Silence noisy libraries
logging.getLogger('playwright').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

# Package exports
__all__ = ['VERSION'] 