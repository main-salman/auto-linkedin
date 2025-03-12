#!/usr/bin/env python3
"""
Run script for Auto LinkedIn application
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path if running directly
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Import from local package
from auto_linkedin.main import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logging.exception("Unhandled exception in main")
        print(f"Error: {str(e)}")
        sys.exit(1) 