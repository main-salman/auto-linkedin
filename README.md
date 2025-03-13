# Auto-LinkedIn
MADE USING [CURSOR AI IDE](https://www.cursor.com/) 

![GitHub License](https://img.shields.io/github/license/main-salman/auto-linkedin)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Playwright](https://img.shields.io/badge/automation-playwright-green)

An advanced Python application for automating LinkedIn interactions. Post content effortlessly to your LinkedIn profile with scheduled posts, media attachments, and more.

![Auto LinkedIn Preview]<img width="1156" alt="image" src="https://github.com/user-attachments/assets/e8071d88-3e0d-4360-8f8a-c1226828945f" />


## ✨ Features

- 📝 **Post Creation**: Create text posts with media attachments (images, videos)
- 📊 **History Tracking**: View and manage your posting history
- 🔄 **Automatic Retry**: Smart retry mechanisms for failed posts


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



