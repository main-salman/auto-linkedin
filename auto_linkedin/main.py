#!/usr/bin/env python3
"""
Main entry point for Auto LinkedIn application
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# Initialize logger
logger = logging.getLogger(__name__)

def main():
    """Main entry point
    
    Returns:
        int: Exit code
    """
    try:
        # Import app runner
        from .app import run_app
        
        # Run application
        return run_app()
    
    except ImportError as e:
        # Handle import errors (missing dependencies)
        print(f"Error: Failed to import required modules: {e}")
        print("Please make sure all dependencies are installed.")
        print("Run: pip install -r requirements.txt")
        return 1
    
    except Exception as e:
        # Handle unexpected errors
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # When running as script, not as module
    sys.exit(main()) 