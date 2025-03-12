"""
Main window UI for the Auto LinkedIn application
"""

import os
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTextEdit, QProgressBar, QLineEdit, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt6.QtGui import QAction, QIcon, QFont, QPixmap

from auto_linkedin.browser.linkedin_controller import LinkedInController
from auto_linkedin.utils.data_loader import DataLoader
from auto_linkedin.ui.login_dialog import LinkedInLoginDialog

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main window of the Auto LinkedIn application"""
    
    def __init__(self, config, linkedin_controller=None, data_loader=None, post_scheduler=None):
        super().__init__()
        self.config = config
        
        # Use provided controllers or create new ones
        self.linkedin = linkedin_controller or LinkedInController()
        self.data_loader = data_loader or DataLoader()
        self.post_scheduler = post_scheduler
        
        self.post_data = []
        self.last_post_index = -1
        self.posting_timer = None
        self.is_paused = False
        
        # Initialize UI
        self.setup_ui()
        
        # Check login status when app starts
        QTimer.singleShot(1000, self.check_login_status)
    
    def update_scheduler_status(self, status):
        """Update the scheduler status in the UI
        
        Args:
            status: Dictionary with status information
        """
        try:
            # Update status in the UI
            is_running = status.get('is_running', False)
            queue_size = status.get('queue_size', 0)
            last_post_time = status.get('last_post_time')
            next_post_time = status.get('next_post_time')
            
            # Log status update
            status_msg = f"Scheduler status: running={is_running}, queue={queue_size}"
            if last_post_time:
                status_msg += f", last post={last_post_time}"
            if next_post_time:
                status_msg += f", next post={next_post_time}"
            
            self.add_to_log(status_msg)
            
            # Update UI elements based on status
            # (Would update status indicators, enable/disable buttons, etc.)
        except Exception as e:
            logger.exception(f"Error updating scheduler status: {str(e)}")
    
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("Auto LinkedIn")
        self.setMinimumSize(1000, 700)
        
        # Create menu bar
        self.setup_menu()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.setup_posting_tab()
        self.setup_history_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Create LinkedIn status indicator in status bar
        self.login_status_label = QLabel("LinkedIn: Not logged in")
        self.login_status_label.setStyleSheet("color: red;")
        self.statusBar().addPermanentWidget(self.login_status_label)
    
    def setup_menu(self):
        """Set up the application menu"""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # Load data action
        load_action = QAction("&Load Data File", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_data_file)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # LinkedIn menu
        linkedin_menu = self.menuBar().addMenu("&LinkedIn")
        
        # Login action
        self.login_action = QAction("&Login to LinkedIn", self)
        self.login_action.triggered.connect(self.prompt_linkedin_login)
        linkedin_menu.addAction(self.login_action)
        
        # Check login action
        check_login_action = QAction("&Check Login Status", self)
        check_login_action.triggered.connect(self.check_login_status)
        linkedin_menu.addAction(check_login_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_posting_tab(self):
        """Set up the posting tab"""
        posting_tab = QWidget()
        self.tab_widget.addTab(posting_tab, "Posting")
        
        layout = QVBoxLayout(posting_tab)
        
        # File selection section
        file_section = QHBoxLayout()
        file_section.addWidget(QLabel("Data File:"))
        
        self.file_path_label = QLineEdit()
        self.file_path_label.setReadOnly(True)
        self.file_path_label.setPlaceholderText("No file selected")
        file_section.addWidget(self.file_path_label, 1)
        
        self.select_file_btn = QPushButton("Select File")
        self.select_file_btn.clicked.connect(self.load_data_file)
        file_section.addWidget(self.select_file_btn)
        
        layout.addLayout(file_section)
        
        # Data preview
        layout.addWidget(QLabel("Data Preview:"))
        
        self.data_table = QTableWidget(0, 3)  # rows, columns
        self.data_table.setHorizontalHeaderLabels(["Text", "Image", "Status"])
        self.data_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.data_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.data_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.data_table)
        
        # Posting interval section
        interval_section = QHBoxLayout()
        interval_section.addWidget(QLabel("Posting Interval:"))
        
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 1440)  # 1 minute to 24 hours
        self.interval_spinbox.setValue(60)  # Default 60 minutes
        self.interval_spinbox.setSuffix(" minutes")
        interval_section.addWidget(self.interval_spinbox)
        
        interval_section.addStretch(1)
        
        # Media selection
        interval_section.addWidget(QLabel("Media:"))
        self.media_combo = QComboBox()
        self.media_combo.addItems(["Include Media", "Skip Media"])
        interval_section.addWidget(self.media_combo)
        
        layout.addLayout(interval_section)
        
        # Control buttons
        button_section = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Posting Schedule")
        self.start_btn.clicked.connect(self.start_posting_schedule)
        button_section.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("Pause Schedule")
        self.pause_btn.clicked.connect(self.pause_posting)
        self.pause_btn.setEnabled(False)
        button_section.addWidget(self.pause_btn)
        
        self.resume_btn = QPushButton("Resume Schedule")
        self.resume_btn.clicked.connect(self.resume_posting)
        self.resume_btn.setEnabled(False)
        button_section.addWidget(self.resume_btn)
        
        self.post_now_btn = QPushButton("Post Now")
        self.post_now_btn.clicked.connect(self.post_now)
        button_section.addWidget(self.post_now_btn)
        
        layout.addLayout(button_section)
        
        # Log section
        layout.addWidget(QLabel("Activity Log:"))
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Add initial log message
        self.add_to_log("Application started. Please select a data file to begin.")
    
    def setup_history_tab(self):
        """Set up the history tab"""
        history_tab = QWidget()
        self.tab_widget.addTab(history_tab, "History")
        
        layout = QVBoxLayout(history_tab)
        
        # History table
        self.history_table = QTableWidget(0, 4)  # rows, columns
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Text", "Image", "Status"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.history_table)
        
        # Button to clear history
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_history_btn)
    
    def setup_settings_tab(self):
        """Set up the settings tab"""
        settings_tab = QWidget()
        self.tab_widget.addTab(settings_tab, "Settings")
        
        layout = QVBoxLayout(settings_tab)
        
        # LinkedIn login section
        login_section = QHBoxLayout()
        login_section.addWidget(QLabel("LinkedIn Login:"))
        
        self.login_status_indicator = QLabel("Not logged in")
        self.login_status_indicator.setStyleSheet("color: red; font-weight: bold;")
        login_section.addWidget(self.login_status_indicator)
        
        login_section.addStretch(1)
        
        self.check_login_btn = QPushButton("Check Login Status")
        self.check_login_btn.clicked.connect(self.check_login_status)
        login_section.addWidget(self.check_login_btn)
        
        self.login_btn = QPushButton("Login to LinkedIn")
        self.login_btn.clicked.connect(self.prompt_linkedin_login)
        login_section.addWidget(self.login_btn)
        
        layout.addLayout(login_section)
        
        # Browser settings
        layout.addWidget(QLabel("Browser Settings:"))
        
        browser_section = QHBoxLayout()
        browser_section.addWidget(QLabel("User Data Directory:"))
        
        self.user_data_dir = QLineEdit()
        self.user_data_dir.setText(os.path.expanduser("~/.auto_linkedin_browser"))
        self.user_data_dir.setReadOnly(True)
        browser_section.addWidget(self.user_data_dir, 1)
        
        clear_browser_data_btn = QPushButton("Clear Browser Data")
        clear_browser_data_btn.clicked.connect(self.clear_browser_data)
        browser_section.addWidget(clear_browser_data_btn)
        
        layout.addLayout(browser_section)
        
        # User agent setting
        ua_section = QHBoxLayout()
        ua_section.addWidget(QLabel("User Agent:"))
        
        self.user_agent_edit = QLineEdit()
        self.user_agent_edit.setText("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        ua_section.addWidget(self.user_agent_edit, 1)
        
        reset_ua_btn = QPushButton("Reset")
        reset_ua_btn.clicked.connect(self.reset_user_agent)
        ua_section.addWidget(reset_ua_btn)
        
        layout.addLayout(ua_section)
        
        # Apply button
        apply_settings_btn = QPushButton("Apply Settings")
        apply_settings_btn.clicked.connect(self.apply_settings)
        layout.addWidget(apply_settings_btn)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
    
    def load_data_file(self):
        """Load data file with posts"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "",
            "Data Files (*.xlsx *.csv);;Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            self.file_path_label.setText(file_path)
            self.add_to_log(f"Loading data from: {file_path}")
            
            self.post_data = self.data_loader.load_file(file_path)
            self.update_data_table()
            
            self.add_to_log(f"Loaded {len(self.post_data)} posts from data file")
            self.statusBar().showMessage(f"Loaded {len(self.post_data)} posts", 5000)
        except Exception as e:
            self.add_to_log(f"Error loading data file: {str(e)}", "error")
            QMessageBox.critical(self, "Error", f"Failed to load data file: {str(e)}")
    
    def update_data_table(self):
        """Update the data table with post data"""
        self.data_table.setRowCount(0)  # Clear table
        
        for i, post in enumerate(self.post_data):
            row_position = self.data_table.rowCount()
            self.data_table.insertRow(row_position)
            
            # Text column
            text_item = QTableWidgetItem(post.get('text', '')[:50] + '...' if len(post.get('text', '')) > 50 else post.get('text', ''))
            self.data_table.setItem(row_position, 0, text_item)
            
            # Image column
            image_path = post.get('image', 'None')
            image_item = QTableWidgetItem(os.path.basename(image_path) if image_path else 'None')
            self.data_table.setItem(row_position, 1, image_item)
            
            # Status column
            status_item = QTableWidgetItem("Pending")
            self.data_table.setItem(row_position, 2, status_item)
    
    def start_posting_schedule(self):
        """Start the scheduled posting"""
        if not self.post_data:
            QMessageBox.warning(self, "Warning", "No post data loaded. Please select a data file first.")
            return
        
        # Check if we're logged in
        self.check_login_status()
        
        interval_minutes = self.interval_spinbox.value()
        
        # Convert to milliseconds for QTimer
        interval_ms = interval_minutes * 60 * 1000
        
        self.add_to_log(f"Starting posting schedule with {interval_minutes} minute interval")
        
        # Create timer if it doesn't exist
        if not self.posting_timer:
            self.posting_timer = QTimer()
            self.posting_timer.timeout.connect(self.post_scheduled_item)
        
        # Configure and start timer
        self.posting_timer.setInterval(interval_ms)
        self.posting_timer.start()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.resume_btn.setEnabled(False)
        
        # Post first item immediately
        QTimer.singleShot(1000, self.post_scheduled_item)
    
    def pause_posting(self):
        """Pause the posting schedule"""
        if self.posting_timer and self.posting_timer.isActive():
            self.posting_timer.stop()
            self.is_paused = True
            
            self.add_to_log("Posting schedule paused")
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)
    
    def resume_posting(self):
        """Resume the posting schedule"""
        if self.posting_timer and not self.posting_timer.isActive():
            self.posting_timer.start()
            self.is_paused = False
            
            self.add_to_log("Posting schedule resumed")
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)
    
    def post_now(self):
        """Post the next item immediately"""
        if not self.post_data:
            QMessageBox.warning(self, "Warning", "No post data loaded. Please select a data file first.")
            return
        
        self.post_scheduled_item()
    
    def post_scheduled_item(self):
        """Post the next scheduled item"""
        # Check login status first
        login_status = self.linkedin.check_login_status()
        
        if not login_status.get('isLoggedIn', False):
            self.add_to_log("Not logged in to LinkedIn. Please log in before posting.", "error")
            
            if self.posting_timer and self.posting_timer.isActive():
                self.posting_timer.stop()
                self.is_paused = True
                self.pause_btn.setEnabled(False)
                self.resume_btn.setEnabled(True)
            
            # Show login dialog
            self.prompt_linkedin_login()
            return
        
        # Get next post
        next_index = (self.last_post_index + 1) % len(self.post_data)
        post = self.post_data[next_index]
        
        self.add_to_log(f"Posting item {next_index + 1} of {len(self.post_data)}")
        
        # Check if we should skip media
        skip_media = self.media_combo.currentText() == "Skip Media"
        
        # Post to LinkedIn
        try:
            # Get media files if any and if not skipping
            media_files = []
            if not skip_media and post.get('image'):
                image_path = post.get('image')
                if os.path.exists(image_path):
                    media_files.append(image_path)
                else:
                    self.add_to_log(f"Warning: Image file not found: {image_path}", "warning")
            
            result = self.linkedin.post_to_linkedin(post.get('text', ''), media_files)
            
            if result.get('success', False):
                self.add_to_log(f"Successfully posted item {next_index + 1}", "success")
                self.update_post_status(next_index, "Posted")
                self.add_to_history(post, "Posted")
            else:
                self.add_to_log(f"Failed to post item {next_index + 1}: {result.get('message', 'Unknown error')}", "error")
                self.update_post_status(next_index, "Failed")
                self.add_to_history(post, "Failed")
        except Exception as e:
            self.add_to_log(f"Error posting to LinkedIn: {str(e)}", "error")
            self.update_post_status(next_index, "Error")
            self.add_to_history(post, f"Error: {str(e)}")
        
        # Update last posted index
        self.last_post_index = next_index
    
    def update_post_status(self, index, status):
        """Update the status of a post in the data table"""
        if 0 <= index < self.data_table.rowCount():
            status_item = QTableWidgetItem(status)
            
            if status == "Posted":
                status_item.setBackground(Qt.GlobalColor.green)
            elif status == "Failed" or status.startswith("Error"):
                status_item.setBackground(Qt.GlobalColor.red)
            
            self.data_table.setItem(index, 2, status_item)
    
    def add_to_history(self, post, status):
        """Add a post to the history table"""
        from datetime import datetime
        
        row_position = self.history_table.rowCount()
        self.history_table.insertRow(row_position)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_table.setItem(row_position, 0, QTableWidgetItem(timestamp))
        
        # Text
        text = post.get('text', '')[:50] + '...' if len(post.get('text', '')) > 50 else post.get('text', '')
        self.history_table.setItem(row_position, 1, QTableWidgetItem(text))
        
        # Image
        image_path = post.get('image', 'None')
        self.history_table.setItem(row_position, 2, QTableWidgetItem(os.path.basename(image_path) if image_path else 'None'))
        
        # Status
        status_item = QTableWidgetItem(status)
        if status == "Posted":
            status_item.setBackground(Qt.GlobalColor.green)
        elif status == "Failed" or status.startswith("Error"):
            status_item.setBackground(Qt.GlobalColor.red)
        self.history_table.setItem(row_position, 3, status_item)
    
    def clear_history(self):
        """Clear the posting history"""
        reply = QMessageBox.question(
            self,
            "Confirm Clear History",
            "Are you sure you want to clear all posting history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history_table.setRowCount(0)
            self.add_to_log("Posting history cleared")
    
    def check_login_status(self):
        """Check LinkedIn login status"""
        self.add_to_log("Checking LinkedIn login status...")
        
        try:
            result = self.linkedin.check_login_status()
            
            if result.get('isLoggedIn', False):
                self.add_to_log("Successfully logged in to LinkedIn", "success")
                self.login_status_indicator.setText("Logged In")
                self.login_status_indicator.setStyleSheet("color: green; font-weight: bold;")
                self.login_status_label.setText("LinkedIn: Logged in")
                self.login_status_label.setStyleSheet("color: green;")
                self.login_action.setText("Logout from LinkedIn")
            else:
                self.add_to_log(f"Not logged in to LinkedIn: {result.get('message', '')}", "warning")
                self.login_status_indicator.setText("Not Logged In")
                self.login_status_indicator.setStyleSheet("color: red; font-weight: bold;")
                self.login_status_label.setText("LinkedIn: Not logged in")
                self.login_status_label.setStyleSheet("color: red;")
                self.login_action.setText("Login to LinkedIn")
            
            return result.get('isLoggedIn', False)
        except Exception as e:
            self.add_to_log(f"Error checking LinkedIn login status: {str(e)}", "error")
            self.login_status_indicator.setText("Error")
            self.login_status_indicator.setStyleSheet("color: red; font-weight: bold;")
            self.login_status_label.setText("LinkedIn: Error")
            self.login_status_label.setStyleSheet("color: red;")
            return False
    
    def prompt_linkedin_login(self):
        """Prompt the user to log in to LinkedIn"""
        self.add_to_log("Opening LinkedIn login window...")
        
        try:
            # Use a dialog to guide the user
            dialog = LinkedInLoginDialog(self.linkedin, self)
            result = dialog.exec()
            
            if result:
                # Re-check login status
                self.check_login_status()
            else:
                self.add_to_log("LinkedIn login cancelled or failed", "warning")
        except Exception as e:
            self.add_to_log(f"Error opening LinkedIn login window: {str(e)}", "error")
    
    def clear_browser_data(self):
        """Clear browser data"""
        reply = QMessageBox.question(
            self,
            "Confirm Clear Browser Data",
            "Are you sure you want to clear all browser data? This will log you out of LinkedIn.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.linkedin.clear_browser_data()
                self.add_to_log("Browser data cleared", "success")
                self.check_login_status()
            except Exception as e:
                self.add_to_log(f"Error clearing browser data: {str(e)}", "error")
    
    def reset_user_agent(self):
        """Reset user agent to default"""
        default_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.user_agent_edit.setText(default_ua)
    
    def apply_settings(self):
        """Apply settings"""
        try:
            # Apply browser settings
            self.linkedin.set_user_data_dir(self.user_data_dir.text())
            self.linkedin.set_user_agent(self.user_agent_edit.text())
            
            self.add_to_log("Settings applied successfully", "success")
        except Exception as e:
            self.add_to_log(f"Error applying settings: {str(e)}", "error")
    
    def add_to_log(self, message, level="info"):
        """Add a message to the log text box"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Color based on message level
        color = "black"
        if level == "error":
            color = "red"
        elif level == "warning":
            color = "orange"
        elif level == "success":
            color = "green"
        
        formatted_message = f"<span style='color:{color}'><b>[{timestamp}]</b> {message}</span>"
        
        # Add message to log
        self.log_text.append(formatted_message)
        
        # Also log to console
        logger.info(message)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Auto LinkedIn",
            """<h1>Auto LinkedIn</h1>
            <p>Version 1.0.0</p>
            <p>A Python application for LinkedIn automation.</p>
            <p>© 2023 All rights reserved.</p>"""
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.posting_timer and self.posting_timer.isActive():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "A posting schedule is active. Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Clean up resources
                self.linkedin.close_browser()
                event.accept()
            else:
                event.ignore()
        else:
            # Clean up resources
            self.linkedin.close_browser()
            event.accept() 