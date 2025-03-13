# Auto-LinkedIn
MADE USING [CURSOR AI IDE](https://www.cursor.com/) 

![GitHub License](https://img.shields.io/github/license/main-salman/auto-linkedin)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Playwright](https://img.shields.io/badge/automation-playwright-green)

An advanced Python application for automating LinkedIn interactions. Post content effortlessly to your LinkedIn profile with scheduled posts, media attachments, and more.

![Auto LinkedIn Preview]<img width="1156" alt="image" src="https://github.com/user-attachments/assets/e8071d88-3e0d-4360-8f8a-c1226828945f" />


## ✨ Features

- 🔒 **Secure Authentication**: Log in to LinkedIn securely using Playwright browser automation
- 📝 **Post Creation**: Create text posts with media attachments (images, videos)
- ⏱️ **Scheduling**: Schedule posts for future publication with flexible timing options
- 📊 **History Tracking**: View and manage your posting history
- 🔄 **Automatic Retry**: Smart retry mechanisms for failed posts
- 🌐 **Modern UI**: Intuitive PyQt-based graphical user interface
- 🛡️ **Browser Stealth**: Advanced browser fingerprint protection measures

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Install from source

1. Clone the repository
   ```bash
   git clone https://github.com/main-salman/auto-linkedin.git
   cd auto-linkedin
   ```

2. Install the package and dependencies
   ```bash
   pip install -e .
   ```
   
   Or directly install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers
   ```bash
   python -m playwright install chromium
   ```

## 📋 Usage

### Running the application

```bash
python run.py
```

Or if installed as a package:

```bash
auto-linkedin
```

### First-time setup

1. Launch the application using the command above
2. The application will automatically open a browser window for LinkedIn login
3. Log in to your LinkedIn account in the opened browser
4. Once logged in successfully, the status in the application will update
5. You can now create and schedule posts

### Creating a post

1. In the application, go to the "Create Post" tab
2. Enter your post text in the text editor
3. To add media, click "Add Media" and select files from your computer
4. Set a publication date and time if you want to schedule the post
5. Click "Post Now" to publish immediately or "Schedule" to add it to the queue

### Managing scheduled posts

1. Go to the "Scheduled Posts" tab to view upcoming posts
2. You can edit, delete, or manually trigger scheduled posts
3. The application will automatically publish scheduled posts at the designated time

## 🔧 Configuration

The application stores its configuration in `~/.auto_linkedin_config.json`. This includes:

- Browser user data directory path (for persisting login sessions)
- User interface settings
- Scheduling preferences

You can modify settings through the application's Settings tab.

## 🛠️ Development

### Setting up a development environment

```bash
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Project Structure

```
auto-linkedin/
├── auto_linkedin/           # Main package
│   ├── browser/             # Browser automation components
│   ├── ui/                  # User interface components
│   ├── utils/               # Utility functions and helpers
│   ├── app.py               # Application core
│   └── scheduler.py         # Post scheduling system
├── docs/                    # Documentation
├── tests/                   # Test suite
├── run.py                   # Entry point script
├── setup.py                 # Package setup
└── requirements.txt         # Dependencies
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Acknowledgements

- [Playwright](https://playwright.dev) for browser automation
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework
- [LinkedIn](https://www.linkedin.com) for their platform 



# Auto-LinkedIn Installation Guide

Thank you for downloading Auto-LinkedIn! This guide will help you install and run the application.

## Windows Installation

1. **Extract the ZIP file** to a location of your choice
2. **Run the browser setup**:
   - Double-click on `install_browser.bat`
   - Wait for the Playwright browser installation to complete
3. **Launch the application**:
   - Double-click on `Auto-LinkedIn.exe`
   - If Windows SmartScreen shows a warning, click "More info" and then "Run anyway"

## Mac Installation

1. **Extract the ZIP file** to your Applications folder or another location
2. **Run the browser setup**:
   - Open Terminal
   - Drag and drop `install_browser.sh` into the Terminal window
   - Press Enter to run the script
   - Enter your password if prompted
   - Wait for the Playwright browser installation to complete
3. **Launch the application**:
   - Control-click on `Auto-LinkedIn` and select "Open"
   - At the security warning, click "Open"
   - The first time you run the app, macOS may require additional permissions

## First-Time Setup

1. When you first run Auto-LinkedIn, you'll need to log in to your LinkedIn account
2. The application will open a browser window automatically
3. Log in to your LinkedIn account in the browser
4. Once logged in, the application will show "Connected to LinkedIn"

## Sample Data

A sample data file (`sample_data.csv`) is included in the `resources` folder. You can use this to test posting with the application.

## Troubleshooting

### Browser Not Installing

If the browser installation script fails:

1. Ensure you have Python 3.9 or higher installed
2. Open a command prompt (Windows) or Terminal (Mac)
3. Navigate to the application folder
4. Run: `python -m playwright install chromium`

### Application Crashes on Start

This might be due to missing browser files:

1. Run the browser installation script again
2. Ensure you have an active internet connection
3. Check if your antivirus is blocking the application

### Login Issues

If you're having trouble logging in to LinkedIn:

1. Try logging in manually in a normal browser first
2. Check if your account has two-factor authentication enabled
3. The application will wait for you to complete any security challenges

## Need Help?

If you encounter any issues, please report them on our GitHub repository:
https://github.com/main-salman/auto-linkedin/issues
```
Let's now create a deployment script to help with packaging and distributing the executables:

```python:package.py
#!/usr/bin/env python3
"""
Packaging script for Auto LinkedIn
Creates distributable ZIP files for Windows and Mac
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from datetime import datetime

# Run the build script first
print("Building executables...")
subprocess.check_call([sys.executable, "build.py"])

# Configuration
APP_NAME = "Auto-LinkedIn"
VERSION = None

# Get version from version.py
version_file = os.path.join("auto_linkedin", "version.py")
if os.path.exists(version_file):
    with open(version_file, "r") as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                VERSION = line.split("=")[1].strip().strip('"\'')
                break

if not VERSION:
    VERSION = "1.0.0"  # Default version if not found

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
package_dir = os.path.join(output_dir, package_name)

# Copy distribution files to package directory
print(f"Creating package directory: {package_dir}")
if os.path.exists(package_dir):
    shutil.rmtree(package_dir)
os.makedirs(package_dir)

# Copy all files from dist directory
print("Copying distribution files...")
for item in os.listdir("dist"):
    src = os.path.join("dist", item)
    dst = os.path.join(package_dir, item)
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

# Copy additional files
print("Copying documentation...")
for file in ["README.md", "LICENSE", "INSTALLATION.md"]:
    if os.path.exists(file):
        shutil.copy2(file, package_dir)

# Create ZIP file
zip_file = os.path.join(output_dir, f"{package_name}.zip")
print(f"Creating ZIP file: {zip_file}")
shutil.make_archive(os.path.join(output_dir, package_name), 'zip', package_dir)

# Clean up package directory
shutil.rmtree(package_dir)

print(f"Package created: {zip_file}")
print("Done!")
```
Let's make these scripts executable:

```bash
chmod +x build.py package.py
```
I see you're on Windows where the chmod command doesn't work. Let's modify these scripts to ensure they're executable on Windows:

```batch:build_windows.bat
@echo off
echo Building Auto-LinkedIn executable for Windows...
python build.py
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)
echo Build completed successfully!
pause
```

```batch:package_windows.bat
@echo off
echo Packaging Auto-LinkedIn for distribution...
python package.py
if errorlevel 1 (
    echo Packaging failed!
    pause
    exit /b 1
)
echo Packaging completed successfully!
echo The distributable package is in the 'packages' folder.
pause
```
Now let's create a simple README for the build instructions:

```markdown:BUILD_INSTRUCTIONS.md
# Build Instructions for Auto-LinkedIn

These instructions will help you build distributable executables for Auto-LinkedIn.

## Prerequisites

- Python 3.9 or higher
- All dependencies installed (`pip install -r requirements.txt`)
- PyInstaller (`pip install pyinstaller>=6.10.0`)

## Building on Windows

1. Run the build script by double-clicking `build_windows.bat` or running it from the command line:
   ```
   build_windows.bat
   ```

2. To create a distributable package, run:
   ```
   package_windows.bat
   ```

3. The executable will be in the `dist` folder, and the packaged ZIP file will be in the `packages` folder.

## Building on macOS/Linux

1. Make the build script executable:
   ```
   chmod +x build.py
   ```

2. Run the build script:
   ```
   ./build.py
   ```

3. Make the package script executable:
   ```
   chmod +x package.py
   ```

4. Create a distributable package:
   ```
   ./package.py
   ```

5. The executable will be in the `dist` folder, and the packaged ZIP file will be in the `packages` folder.

## Customizing the Build

You can customize the build by editing the `build.py` file. Here are some common customizations:

- Change the application name: Modify `APP_NAME` variable
- Add additional hidden imports: Add to the `pyinstaller_args` list
- Change icon: Create your own `.ico` file and update the `ICON_PATH` variable

## Troubleshooting

If you encounter issues:

1. **Missing modules**: Add them as hidden imports in the `build.py` file
2. **File not found errors**: Make sure all required files are included in the `--add-data` parameter
3. **Playwright issues**: Check that the browser installation script is working properly

## Creating Signed Packages

For distribution in app stores or to avoid security warnings:

### macOS

1. Create an Apple Developer account
2. Obtain a Developer ID certificate
3. Sign the app using:
   ```
   codesign --force --deep --sign "Developer ID Application: Your Name" "dist/Auto-LinkedIn.app"
   ```

### Windows

1. Obtain a code signing certificate from a trusted Certificate Authority
2. Sign the executable with:
   ```
   signtool sign /fd SHA256 /f cert.pfx /p password "dist\Auto-LinkedIn.exe"
   ```
```
Now let's verify we have all the necessary files for building our executable:

Ran tool
Let's create a simple icon for the application:

```python:build.py
# Configuration
APP_NAME = "Auto-LinkedIn"
ENTRY_POINT = "run.py"
ICON_PATH = None  # No icon available yet, update this path when you have an icon
VERSION = None
```
Let's test the build process with a simple command:

```bash
python -c "import PyInstaller; print(f'PyInstaller version: {PyInstaller.__version__}')"
```
Great! Now let's create a PowerShell script that will guide users through building the executable on Windows:

```powershell:build-exe.ps1
# Auto-LinkedIn Build Script
# This PowerShell script guides through building the executable

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "It's recommended to run this script as Administrator." -ForegroundColor Yellow
    Write-Host "Some operations may fail without admin privileges." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (Y/N)"
    if ($continue -ne "Y") {
        exit
    }
}

# Set the execution policy to allow running PowerShell scripts
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
} catch {
    Write-Host "Could not set execution policy. Continuing anyway..." -ForegroundColor Yellow
}

# Check Python version
try {
    $pythonVersion = python --version
    Write-Host "Using $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.9 or higher." -ForegroundColor Red
    exit
}

# Ensure pip is up to date
Write-Host "Ensuring pip is up to date..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Check if virtual environment exists, create if not
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    if (-not $?) {
        Write-Host "Failed to create virtual environment. Please install venv with: pip install virtualenv" -ForegroundColor Red
        exit
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Cyan
pip install -r requirements.txt
if (-not $?) {
    Write-Host "Failed to install requirements." -ForegroundColor Red
    exit
}

# Install PyInstaller
Write-Host "Installing PyInstaller..." -ForegroundColor Cyan
pip install pyinstaller>=6.10.0
if (-not $?) {
    Write-Host "Failed to install PyInstaller." -ForegroundColor Red
    exit
}

# Run build script
Write-Host "Running build script..." -ForegroundColor Cyan
python build.py
if (-not $?) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit
}

# Run package script
Write-Host "Packaging the application..." -ForegroundColor Cyan
python package.py
if (-not $?) {
    Write-Host "Packaging failed!" -ForegroundColor Red
    exit
}

# Success message
Write-Host "`nBuild completed successfully!" -ForegroundColor Green
Write-Host "Executable is in the 'dist' folder." -ForegroundColor Green
Write-Host "Packaged ZIP is in the 'packages' folder." -ForegroundColor Green
Write-Host "`nTo run the application, navigate to 'dist' and run 'Auto-LinkedIn.exe'" -ForegroundColor Cyan
Write-Host "Remember to install the Playwright browser by running 'install_browser.bat'" -ForegroundColor Cyan

# Deactivate virtual environment
deactivate

# Wait for user confirmation
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
```
Great! You now have everything you need to create shareable executables for both Windows and Mac. Here's how to do it:

## Windows Instructions:

1. **Use the PowerShell build script (easiest method)**:
   - Right-click on `build-exe.ps1` and select "Run with PowerShell"
   - This script will set up a virtual environment, install all dependencies, and build the executable
   - You'll find the executable in the `dist` folder and a packaged ZIP in the `packages` folder

2. **Alternative method with batch files**:
   - First run `build_windows.bat` to create the executable
   - Then run `package_windows.bat` to create a distributable ZIP package
   - The package will be in the `packages` folder

## Mac Instructions:

1. Open Terminal and navigate to your project directory
2. Make the scripts executable:
   ```
   chmod +x build.py package.py
   ```
3. Run the build script:
   ```
   ./build.py
   ```
4. Run the packaging script:
   ```
   ./package.py
   ```
5. The executable will be in the `dist` folder and the ZIP package will be in the `packages` folder

## Distribution:

When sharing the application with others:

1. Send them the ZIP package from the `packages` folder
2. Include the `INSTALLATION.md` file which provides step-by-step instructions
3. Remind users that they need to run the `install_browser.bat` (Windows) or `install_browser.sh` (Mac) script after installation to set up the Playwright browser

## Customization:

If you want to customize the build process:
- Add an icon by creating a `.ico` file and updating the `ICON_PATH` in `build.py`
- Modify the `build.py` script to include additional files or hidden imports
- Update the version number in `auto_linkedin/version.py` to change the package version

## Important Notes:

1. The executable will be around 60-100 MB in size due to including Python and all dependencies
2. Users won't need to install Python or any dependencies since everything is bundled
3. The first run of the application will install the Playwright browser, which requires internet access
4. Users may see security warnings when running the executable (this is normal for unsigned applications)

Would you like me to help you run the build process now or explain any specific part in more detail?
