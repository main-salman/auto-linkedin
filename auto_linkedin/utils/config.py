"""
Configuration management for Auto LinkedIn
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for Auto LinkedIn"""
    
    def __init__(self, config_file=None):
        """Initialize configuration manager"""
        # Default configuration file
        if config_file is None:
            self.config_file = os.path.expanduser("~/.auto_linkedin_config.json")
        else:
            self.config_file = config_file
        
        # Default configuration
        self.defaults = {
            "user_data_dir": os.path.expanduser("~/.auto_linkedin_browser"),
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "posting_interval_minutes": 60,
            "skip_media": False,
            "last_posted_index": -1,
            "is_paused": False,
            "last_file_path": "",
            "history": [],
            "errors": []
        }
        
        # Load configuration
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        # Start with default configuration
        config = self.defaults.copy()
        
        # Try to load from file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    file_config = json.load(f)
                
                # Update config with values from file
                config.update(file_config)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        else:
            logger.info(f"No configuration file found at {self.config_file}")
            self.save_config(config)
        
        return config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved configuration to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value"""
        self.config[key] = value
        return self.save_config()
    
    def add_to_history(self, post, status):
        """Add a post to history"""
        timestamp = datetime.now().isoformat()
        
        history_item = {
            "timestamp": timestamp,
            "text": post.get("text", "")[:100],
            "image": post.get("image", ""),
            "status": status
        }
        
        if "history" not in self.config:
            self.config["history"] = []
        
        self.config["history"].append(history_item)
        self.save_config()
    
    def add_error(self, message):
        """Add an error message"""
        timestamp = datetime.now().isoformat()
        
        error_item = {
            "timestamp": timestamp,
            "message": message
        }
        
        if "errors" not in self.config:
            self.config["errors"] = []
        
        self.config["errors"].append(error_item)
        self.save_config()
    
    def clear_history(self):
        """Clear posting history"""
        self.config["history"] = []
        return self.save_config()
    
    def clear_errors(self):
        """Clear error messages"""
        self.config["errors"] = []
        return self.save_config() 