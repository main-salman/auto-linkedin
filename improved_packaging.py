#!/usr/bin/env python3
"""
Improved packaging script for Auto LinkedIn
Creates a ZIP file with all necessary files while handling permissions better
"""

import os
import sys
import shutil
import platform
import zipfile
from datetime import datetime

# Configuration
APP_NAME = "Auto-LinkedIn"
VERSION = "0.1.0-alpha.1"  # Hardcoded version to avoid import issues

print(f"Packaging {APP_NAME} version {VERSION}")

# Create timestamp for the build
timestamp = datetime.now().strftime("%Y%m%d")

# Determine platform
is_windows = platform.system() == "Windows"
is_mac = platform.system() == "Darwin"
platform_name = "windows" if is_windows else "mac" if is_mac else "linux"

# Create output directory
output_dir = "packages"
os.makedirs(output_dir, exist_ok=True)

# Package name
package_name = f"{APP_NAME}-{VERSION}-{platform_name}-{timestamp}"
zip_file = os.path.join(output_dir, f"{package_name}.zip")

# Check if dist directory exists
if not os.path.exists("dist"):
    print("Warning: dist directory not found. Checking if executable exists elsewhere...")
    if is_windows and os.path.exists(os.path.join(".", f"{APP_NAME}.exe")):
        print(f"Found {APP_NAME}.exe in current directory.")
    else:
        print("Error: Executable not found. Run build script first.")
        sys.exit(1)

# Create ZIP file directly
print(f"Creating ZIP file: {zip_file}")
with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # If executable exists in dist directory, add it
    exe_filename = f"{APP_NAME}.exe" if is_windows else APP_NAME
    exe_path = os.path.join("dist", exe_filename)
    if os.path.exists(exe_path):
        print(f"Adding executable: {exe_filename}")
        zipf.write(exe_path, exe_filename)
    elif os.path.exists(exe_filename):
        print(f"Adding executable from current directory: {exe_filename}")
        zipf.write(exe_filename, exe_filename)
    
    # Add browser installation script
    if is_windows:
        if os.path.exists(os.path.join("dist", "install_browser.bat")):
            zipf.write(os.path.join("dist", "install_browser.bat"), "install_browser.bat")
        else:
            print("Creating browser installation script")
            install_script = "@echo off\necho Installing Playwright browsers...\nset \"PLAYWRIGHT_BROWSERS_PATH=%USERPROFILE%\\.cache\\playwright\"\necho Browser cache path set to: %PLAYWRIGHT_BROWSERS_PATH%\npython -m playwright install chromium\necho Installation complete!\npause\n"
            zipf.writestr("install_browser.bat", install_script)
    elif is_mac:
        if os.path.exists(os.path.join("dist", "install_browser.sh")):
            zipf.write(os.path.join("dist", "install_browser.sh"), "install_browser.sh")
        else:
            print("Creating browser installation script")
            install_script = "#!/bin/bash\necho \"Installing Playwright browsers...\"\nexport PLAYWRIGHT_BROWSERS_PATH=\"$HOME/.cache/playwright\"\necho \"Browser cache path set to: $PLAYWRIGHT_BROWSERS_PATH\"\npython -m playwright install chromium\necho \"Installation complete!\"\n"
            zipf.writestr("install_browser.sh", install_script)
    
    # Add README, LICENSE, and INSTALLATION files
    for file in ["README.md", "LICENSE", "INSTALLATION.md"]:
        if os.path.exists(file):
            print(f"Adding: {file}")
            zipf.write(file, file)
    
    # Add sample data
    sample_data_path = "sample_data.csv"
    if os.path.exists(sample_data_path):
        print(f"Adding: {sample_data_path}")
        zipf.write(sample_data_path, os.path.join("resources", "sample_data.csv"))
    elif os.path.exists(os.path.join("dist", "resources", "sample_data.csv")):
        print(f"Adding: resources/sample_data.csv")
        zipf.write(os.path.join("dist", "resources", "sample_data.csv"), 
                  os.path.join("resources", "sample_data.csv"))

print(f"Package created: {zip_file}")
print("Done!") 