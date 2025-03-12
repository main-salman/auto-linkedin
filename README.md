# Auto-LinkedIn

![GitHub License](https://img.shields.io/github/license/main-salman/auto-linkedin)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Playwright](https://img.shields.io/badge/automation-playwright-green)

An advanced Python application for automating LinkedIn interactions. Post content effortlessly to your LinkedIn profile with scheduled posts, media attachments, and more.

![Auto LinkedIn Preview](https://github.com/main-salman/auto-linkedin/raw/main/docs/images/app_preview.png)

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