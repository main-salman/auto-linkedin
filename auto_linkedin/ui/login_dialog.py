"""
LinkedIn login dialog
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QMessageBox, QTextBrowser
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap

logger = logging.getLogger(__name__)

class LinkedInLoginDialog(QDialog):
    """Dialog to guide users through the LinkedIn login process"""
    
    def __init__(self, linkedin, parent=None):
        super().__init__(parent)
        self.linkedin = linkedin
        self.login_successful = False
        self.check_timer = None
        
        self.setWindowTitle("LinkedIn Login")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self.setup_ui()
        
        # Start browser and login process when dialog opens
        QTimer.singleShot(100, self.start_login_process)
    
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # LinkedIn logo
        # logo_label = QLabel()
        # logo_pixmap = QPixmap("path/to/linkedin_logo.png")  # Replace with actual path
        # logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        # logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("LinkedIn Login")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Instructions
        self.instruction_label = QLabel(
            "We will open a browser window for you to log in to LinkedIn.\n"
            "Please log in with your credentials in the browser window."
        )
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.instruction_label)
        
        # Status
        self.status_label = QLabel("Preparing browser...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        # Detailed instructions
        instructions_browser = QTextBrowser()
        instructions_browser.setHtml("""
        <h3>Detailed Instructions:</h3>
        <ol>
            <li>A browser window will open automatically.</li>
            <li>Navigate to LinkedIn.com if not redirected automatically.</li>
            <li>Sign in with your LinkedIn credentials.</li>
            <li>The system will automatically detect when you've successfully logged in.</li>
            <li>If prompted with security checks or CAPTCHA, complete them in the browser.</li>
            <li>Click "Cancel" if you wish to abort the login process.</li>
            <li>The dialog will close automatically once login is detected.</li>
        </ol>
        <p><b>Note:</b> For security reasons, we do not store your LinkedIn password.</p>
        """)
        instructions_browser.setMinimumHeight(150)
        layout.addWidget(instructions_browser)
        
        # Additional tips
        tips_label = QLabel(
            "<b>Tip:</b> If you encounter security warnings, try using the standard login "
            "instead of social login options."
        )
        tips_label.setWordWrap(True)
        tips_label.setStyleSheet("color: #666;")
        layout.addWidget(tips_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.manual_check_btn = QPushButton("Check Login Status")
        self.manual_check_btn.clicked.connect(self.check_login_status)
        self.manual_check_btn.setEnabled(False)
        button_layout.addWidget(self.manual_check_btn)
        
        layout.addLayout(button_layout)
    
    def start_login_process(self):
        """Start the login process"""
        self.status_label.setText("Opening browser window...")
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        try:
            # Prompt login in LinkedIn controller
            result = self.linkedin.prompt_login()
            
            if result.get('success', False):
                self.login_successful = True
                self.status_label.setText("Successfully logged in to LinkedIn!")
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(100)
                
                # Close dialog after a short delay
                QTimer.singleShot(2000, self.accept)
            else:
                # Start checking login status periodically
                self.status_label.setText("Waiting for login completion...")
                self.manual_check_btn.setEnabled(True)
                
                # Start timer to check login status every 3 seconds
                self.check_timer = QTimer()
                self.check_timer.timeout.connect(self.check_login_status)
                self.check_timer.start(3000)
        except Exception as e:
            logger.exception("Error starting login process")
            self.status_label.setText(f"Error: {str(e)}")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open browser for LinkedIn login: {str(e)}"
            )
    
    def check_login_status(self):
        """Check if the user has logged in to LinkedIn"""
        try:
            self.status_label.setText("Checking login status...")
            
            result = self.linkedin.check_login_status()
            
            if result.get('isLoggedIn', False):
                self.login_successful = True
                self.status_label.setText("Successfully logged in to LinkedIn!")
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(100)
                
                # Stop the timer
                if self.check_timer and self.check_timer.isActive():
                    self.check_timer.stop()
                
                # Close dialog after a short delay
                QTimer.singleShot(2000, self.accept)
            else:
                security_challenge = result.get('error') == 'security_challenge'
                
                if security_challenge:
                    self.status_label.setText("Security challenge detected. Please complete it in the browser.")
                else:
                    self.status_label.setText("Waiting for login completion...")
        except Exception as e:
            logger.exception("Error checking login status")
            self.status_label.setText(f"Error checking login status: {str(e)}")
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        # Stop the timer if active
        if self.check_timer and self.check_timer.isActive():
            self.check_timer.stop()
        
        event.accept()
    
    def exec(self):
        """Execute the dialog and return success status"""
        result = super().exec()
        
        # Return True if login was successful
        return self.login_successful 