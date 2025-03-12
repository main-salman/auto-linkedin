"""
Playwright helper module for use with PyInstaller bundled applications
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_playwright_browsers_installed():
    """
    Ensure Playwright browsers are installed and properly configured for PyInstaller.
    This is needed because PyInstaller-packaged applications have a different file structure.
    """
    logger.info("Checking Playwright browser installation...")
    
    # Get the application base directory
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        base_dir = sys._MEIPASS
        is_bundled = True
        logger.info(f"Running as PyInstaller bundle. Base dir: {base_dir}")
    else:
        # Running as regular Python script
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        is_bundled = False
        logger.info(f"Running as regular Python script. Base dir: {base_dir}")
    
    # When running as bundled app, we need to modify PLAYWRIGHT_BROWSERS_PATH
    if is_bundled:
        # Set the Playwright browsers path to user's home directory
        browsers_path = os.path.join(os.path.expanduser("~"), ".cache", "playwright")
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
        logger.info(f"Set PLAYWRIGHT_BROWSERS_PATH to: {browsers_path}")
        
        # Check if browser is installed
        if not os.path.exists(os.path.join(browsers_path, "chromium")):
            logger.warning("Playwright browsers not found in the expected location.")
            logger.info("Please run the install_browser.bat/sh script provided with the application.")
    
    logger.info("Playwright browser check completed") 