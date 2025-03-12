#!/usr/bin/env python3
"""
Build script for Auto LinkedIn (No Clean version)
Creates standalone executables for Windows and Mac without cleaning directories
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

# Configuration
APP_NAME = "Auto-LinkedIn"
ENTRY_POINT = "run.py"
ICON_PATH = None  # No icon available yet, update this path when you have an icon

# Get version from version.py
version_file = os.path.join("auto_linkedin", "version.py")
if os.path.exists(version_file):
    try:
        # Try to import the version directly
        sys.path.insert(0, os.path.abspath('.'))
        from auto_linkedin.version import __version__ as VERSION
    except ImportError:
        # Fallback to parsing the file
        VERSION = "1.0.0"  # Default version
        with open(version_file, "r") as f:
            for line in f.readlines():
                if line.startswith("__version__"):
                    VERSION = line.split("=")[1].strip().strip('"\'')
                    break
else:
    VERSION = "1.0.0"  # Default version if file not found

print(f"Building {APP_NAME} version {VERSION}")

# Determine platform-specific settings
is_windows = platform.system() == "Windows"
is_mac = platform.system() == "Darwin"

# Base PyInstaller command
pyinstaller_args = [
    "--name", APP_NAME,
    "--onefile",  # Create a single executable
    "--windowed",  # Don't show console window
    # Skip the --clean flag to avoid permission issues
    f"--add-data=auto_linkedin{os.pathsep}auto_linkedin",  # Include package data
]

# Add icon if it exists
if ICON_PATH is not None and os.path.exists(ICON_PATH):
    pyinstaller_args.extend(["--icon", ICON_PATH])

# Platform-specific options
if is_windows:
    # Windows-specific options
    pyinstaller_args.extend([
        "--hidden-import=playwright.async_api",
        "--hidden-import=pkg_resources.py2_warn",
        "--hidden-import=packaging.version",
        "--hidden-import=packaging.specifiers",
        "--hidden-import=packaging.requirements",
    ])
elif is_mac:
    # Mac-specific options
    pyinstaller_args.extend([
        "--hidden-import=playwright.async_api",
        "--hidden-import=pkg_resources.py2_warn",
        "--hidden-import=packaging.version",
        "--hidden-import=packaging.specifiers",
        "--hidden-import=packaging.requirements",
        "--osx-bundle-identifier", "com.autolinkedin.app",
    ])

# Add the entry point
pyinstaller_args.append(ENTRY_POINT)

# Run PyInstaller
print("Running PyInstaller with the following arguments:")
print(" ".join(pyinstaller_args))
subprocess.check_call([sys.executable, "-m", "PyInstaller"] + pyinstaller_args)

# After building, copy additional resources
print("Copying additional resources...")

# Create a directory for Playwright browser download
resources_path = os.path.join("dist", "resources")
os.makedirs(resources_path, exist_ok=True)

# Copy sample data
sample_data_path = "sample_data.csv"
if os.path.exists(sample_data_path):
    shutil.copy(sample_data_path, resources_path)

# Copy readme
readme_path = "README.md"
if os.path.exists(readme_path):
    shutil.copy(readme_path, os.path.join("dist"))

# Create a post-installation script for installing Playwright browsers
if is_windows:
    playwright_install_script = os.path.join("dist", "install_browser.bat")
    with open(playwright_install_script, "w") as f:
        f.write('@echo off\n')
        f.write('echo Installing Playwright browsers...\n')
        f.write('set "PLAYWRIGHT_BROWSERS_PATH=%USERPROFILE%\\.cache\\playwright"\n')
        f.write('echo Browser cache path set to: %PLAYWRIGHT_BROWSERS_PATH%\n')
        f.write('python -m playwright install chromium\n')
        f.write('echo Installation complete!\n')
        f.write('pause\n')
elif is_mac:
    playwright_install_script = os.path.join("dist", "install_browser.sh")
    with open(playwright_install_script, "w") as f:
        f.write('#!/bin/bash\n')
        f.write('echo "Installing Playwright browsers..."\n')
        f.write('export PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/playwright"\n')
        f.write('echo "Browser cache path set to: $PLAYWRIGHT_BROWSERS_PATH"\n')
        f.write('python -m playwright install chromium\n')
        f.write('echo "Installation complete!"\n')
    # Make the script executable
    os.chmod(playwright_install_script, 0o755)

print(f"Build completed! Executable created in dist/")
print(f"After distributing, users should run the browser installer script") 