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