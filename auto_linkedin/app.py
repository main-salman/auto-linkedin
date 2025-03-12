"""
Application initialization for Auto LinkedIn
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDir

from .browser import LinkedInController
from .utils import Config, DataLoader
from .utils.playwright_helper import ensure_playwright_browsers_installed
from .ui import MainWindow
from .scheduler import PostScheduler

logger = logging.getLogger(__name__)

class Application:
    """Auto LinkedIn Application"""
    
    def __init__(self, args=None):
        """Initialize the application
        
        Args:
            args: Command line arguments
        """
        self.args = args
        self.config = None
        self.linkedin_controller = None
        self.data_loader = None
        self.post_scheduler = None
        self.app = None
        self.main_window = None
    
    def initialize(self):
        """Initialize the application components
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing application components")
            
            # Create configuration manager
            self.config = Config()
            self.config.load_config()
            
            # Create LinkedIn controller
            self.linkedin_controller = LinkedInController()
            
            # Apply configuration to LinkedIn controller
            user_data_dir = self.config.get('user_data_dir')
            if user_data_dir:
                self.linkedin_controller.set_user_data_dir(os.path.expanduser(user_data_dir))
            
            user_agent = self.config.get('user_agent')
            if user_agent:
                self.linkedin_controller.set_user_agent(user_agent)
            
            # Create data loader
            self.data_loader = DataLoader()
            
            # Create post scheduler
            self.post_scheduler = PostScheduler(self.linkedin_controller, self.config)
            
            logger.info("Application components initialized successfully")
            return True
        
        except Exception as e:
            logger.exception(f"Error initializing application: {str(e)}")
            return False
    
    def create_ui(self):
        """Create the user interface
        
        Returns:
            bool: True if UI creation successful, False otherwise
        """
        try:
            logger.info("Creating application UI")
            
            # Create QApplication instance
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Auto LinkedIn")
            self.app.setOrganizationName("Auto LinkedIn")
            self.app.setOrganizationDomain("autolinkedin.app")
            
            # Set style
            self.app.setStyle("Fusion")
            
            # Create main window
            self.main_window = MainWindow(
                config=self.config,
                linkedin_controller=self.linkedin_controller,
                data_loader=self.data_loader,
                post_scheduler=self.post_scheduler
            )
            
            # Connect scheduler status updates to main window
            self.post_scheduler.set_status_callback(self.main_window.update_scheduler_status)
            
            logger.info("Application UI created successfully")
            return True
        
        except Exception as e:
            logger.exception(f"Error creating application UI: {str(e)}")
            return False
    
    def run(self):
        """Run the application
        
        Returns:
            int: Application exit code
        """
        try:
            logger.info("Starting application")
            
            # Initialize components
            if not self.initialize():
                logger.error("Failed to initialize application components")
                return 1
            
            # Create UI
            if not self.create_ui():
                logger.error("Failed to create application UI")
                return 1
            
            # Show main window
            self.main_window.show()
            
            # Start application event loop
            return self.app.exec()
        
        except Exception as e:
            logger.exception(f"Error running application: {str(e)}")
            return 1
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up application resources"""
        try:
            logger.info("Cleaning up application resources")
            
            # Stop post scheduler
            if self.post_scheduler:
                self.post_scheduler.stop()
            
            # Close browser
            if self.linkedin_controller:
                self.linkedin_controller.close_browser()
            
            # Save configuration
            if self.config:
                self.config.save_config()
            
            logger.info("Application cleanup completed")
        
        except Exception as e:
            logger.exception(f"Error during application cleanup: {str(e)}")


def parse_arguments():
    """Parse command line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Auto LinkedIn - Python application for LinkedIn automation")
    
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (no UI)')
    
    return parser.parse_args()


def setup_logging(debug=False):
    """Configure logging based on command line options
    
    Args:
        debug: Whether to enable debug logging
    """
    # Root logger already configured in __init__.py
    # Just adjust level based on debug flag
    if debug:
        logging.getLogger('auto_linkedin').setLevel(logging.DEBUG)
        logging.getLogger('playwright').setLevel(logging.INFO)  # More verbose for playwright


def run_app():
    """Run the application
    
    Returns:
        int: Application exit code
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.debug)
    
    # Ensure Playwright browsers are properly configured
    # This is especially important for PyInstaller bundles
    ensure_playwright_browsers_installed()
    
    # Create and run application
    application = Application(args)
    return application.run() 