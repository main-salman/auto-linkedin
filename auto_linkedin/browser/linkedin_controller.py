"""
LinkedIn browser controller using Playwright
"""

import os
import time
import logging
import random
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
import sys

logger = logging.getLogger(__name__)

class LinkedInController:
    """Controller for LinkedIn browser automation using Playwright"""
    
    def __init__(self):
        """Initialize LinkedIn controller"""
        self.browser_context = None
        self.page = None
        self.is_initialized = False
        self.playwright = None
        
        # Default settings
        self.user_data_dir = os.path.expanduser("~/.auto_linkedin_browser")
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        
        # Create user data directory if it doesn't exist
        os.makedirs(self.user_data_dir, exist_ok=True)
    
    def set_user_data_dir(self, user_data_dir):
        """Set user data directory"""
        self.user_data_dir = user_data_dir
        os.makedirs(self.user_data_dir, exist_ok=True)
    
    def set_user_agent(self, user_agent):
        """Set user agent string"""
        self.user_agent = user_agent
    
    def check_login_status(self):
        """Check if user is logged in to LinkedIn"""
        try:
            # Initialize browser if needed
            if not self.is_initialized:
                self._run_async(self._init_browser())
            
            # Check login status
            return self._run_async(self._check_login_status())
        except Exception as e:
            logger.exception("Error checking login status")
            return {
                "isLoggedIn": False,
                "error": str(e),
                "message": f"Error checking login status: {str(e)}"
            }
    
    def prompt_login(self):
        """Open LinkedIn login page and wait for user to log in"""
        try:
            # Initialize browser if needed
            if not self.is_initialized:
                self._run_async(self._init_browser())
            
            # Prompt login
            return self._run_async(self._prompt_login())
        except Exception as e:
            logger.exception("Error prompting login")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error prompting login: {str(e)}"
            }
    
    def post_to_linkedin(self, text, media_files=None):
        """Post content to LinkedIn"""
        try:
            # Initialize browser if needed
            if not self.is_initialized:
                self._run_async(self._init_browser())
            
            # Check login status
            login_status = self._run_async(self._check_login_status())
            
            if not login_status.get("isLoggedIn", False):
                return {
                    "success": False,
                    "message": "Not logged in to LinkedIn. Please log in before posting."
                }
            
            # Post to LinkedIn
            return self._run_async(self._post_to_linkedin(text, media_files))
        except Exception as e:
            logger.exception("Error posting to LinkedIn")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error posting to LinkedIn: {str(e)}"
            }
    
    def clear_browser_data(self):
        """Clear browser data"""
        try:
            # Close browser if open
            self._run_async(self._close_browser())
            
            # Remove user data directory
            if os.path.exists(self.user_data_dir):
                shutil.rmtree(self.user_data_dir)
            
            # Recreate user data directory
            os.makedirs(self.user_data_dir, exist_ok=True)
            
            return {
                "success": True,
                "message": "Browser data cleared successfully"
            }
        except Exception as e:
            logger.exception("Error clearing browser data")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error clearing browser data: {str(e)}"
            }
    
    def close_browser(self):
        """Close the browser"""
        try:
            self._run_async(self._close_browser())
            return {
                "success": True,
                "message": "Browser closed successfully"
            }
        except Exception as e:
            logger.exception("Error closing browser")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error closing browser: {str(e)}"
            }
    
    def _run_async(self, coro):
        """Run an asynchronous coroutine"""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    async def _init_browser(self):
        """Initialize the browser"""
        logger.info("Initializing browser")
        
        if self.browser_context:
            logger.info("Browser already initialized")
            return
        
        # Clean up user data directory
        await self._force_cleanup_user_data_dir()
        
        # Initialize Playwright
        self.playwright = await async_playwright().start()
        
        # Launch browser with persistent context
        logger.info(f"Launching browser with user data directory: {self.user_data_dir}")
        
        # Additional arguments for browser
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--window-size=1280,800"
        ]
        
        # When running as PyInstaller bundle, add additional arguments to help browser finding
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            logger.info("Running as PyInstaller bundle - adding special browser arguments")
            # These are important for PyInstaller bundled apps
            browser_args.extend([
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage"
            ])
        
        self.browser_context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
            user_agent=self.user_agent,
            locale="en-US",
            timezone_id="America/Los_Angeles",
            java_script_enabled=True,
            ignore_https_errors=False,
            accept_downloads=True,
            args=browser_args
        )
        
        # Get or create page
        if len(self.browser_context.pages) == 0:
            self.page = await self.browser_context.new_page()
        else:
            self.page = self.browser_context.pages[0]
        
        # Set up page event handlers
        self.page.on("console", lambda msg: logger.info(f"Browser console: {msg.text}"))
        self.page.on("pageerror", lambda err: logger.error(f"Browser page error: {err}"))
        
        # Add anti-detection script
        await self._add_stealth_scripts()
        
        self.is_initialized = True
        logger.info("Browser initialized successfully")
    
    async def _close_browser(self):
        """Close the browser"""
        logger.info("Closing browser")
        
        if self.browser_context:
            await self.browser_context.close()
            self.browser_context = None
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        
        self.page = None
        self.is_initialized = False
        
        logger.info("Browser closed")
    
    async def _force_cleanup_user_data_dir(self):
        """Force cleanup of user data directory"""
        logger.info(f"Cleaning up user data directory: {self.user_data_dir}")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.user_data_dir, exist_ok=True)
            
            # Remove lock files
            lock_file = os.path.join(self.user_data_dir, "SingletonLock")
            if os.path.exists(lock_file):
                os.unlink(lock_file)
                logger.info("Removed SingletonLock file")
            
            # Check for other lock files
            lock_files = [
                "SingletonCookie",
                "SingletonSocket",
                ".com.google.Chrome.EUw8Uk",
                "CrashpadMetrics.pma",
                "Local State.bad"
            ]
            
            for file in lock_files:
                file_path = os.path.join(self.user_data_dir, file)
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    logger.info(f"Removed {file}")
        except Exception as e:
            logger.error(f"Error cleaning up user data directory: {str(e)}")
    
    async def _add_stealth_scripts(self):
        """Add scripts to evade detection"""
        logger.info("Adding stealth scripts")
        
        await self.page.add_init_script("""
        // Overwrite the automation flag
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        
        // Make navigator.plugins and navigator.languages look normal
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                const plugins = [1, 2, 3, 4, 5];
                plugins.refresh = () => {};
                plugins.item = () => { return {}; };
                plugins.namedItem = () => { return {}; };
                plugins.length = 5;
                return plugins;
            }
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Prevent fingerprinting via canvas
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(contextType, ...args) {
            const context = originalGetContext.apply(this, [contextType, ...args]);
            if (contextType === '2d') {
                const originalFillText = context.fillText;
                context.fillText = function(...args) {
                    return originalFillText.apply(this, [...args]);
                };
            }
            return context;
        };
        """)
    
    async def _wait_for_human_delay(self, min_delay=500, max_delay=1500):
        """Wait for a human-like delay"""
        delay = random.randint(min_delay, max_delay)
        await asyncio.sleep(delay / 1000)  # Convert to seconds
    
    async def _check_login_status(self):
        """Check if user is logged in to LinkedIn"""
        logger.info("Checking LinkedIn login status")
        
        try:
            # Navigate to LinkedIn homepage
            await self.page.goto(
                url="https://www.linkedin.com/",
                wait_until="domcontentloaded",
                timeout=15000
            )
            
            # Wait for page to load
            await self._wait_for_human_delay(2000, 3000)
            
            # Check for security challenges
            security_check = await self._detect_security_challenges()
            if security_check.get("hasSecurityChallenge", False):
                logger.warning(f"Security challenge detected: {security_check.get('message', '')}")
                return {
                    "isLoggedIn": False,
                    "error": "security_challenge",
                    "message": security_check.get('message', 'Security challenge detected')
                }
            
            # Check login status
            login_status = await self.page.evaluate("""
            () => {
                // Multiple login indicators with fallbacks
                
                // 1. Navigation elements check
                const navCheck = {
                    // Profile elements
                    hasProfilePhoto: !!document.querySelector('.global-nav__me-photo'),
                    hasProfileMenu: !!document.querySelector('.global-nav__me'),
                    
                    // Navigation elements 
                    hasNavMenu: !!document.querySelector('.global-nav__primary-items'),
                    hasMyNetwork: !!document.querySelector('a[href="/mynetwork/"]'),
                    hasJobs: !!document.querySelector('a[href="/jobs/"]'),
                    hasMessaging: !!document.querySelector('a[href="/messaging/"]'),
                    
                    // Feed elements
                    hasFeed: !!document.querySelector('.feed-shared-update-v2') || 
                            !!document.querySelector('.feed-shared-news-module'),
                    
                    // Post creation elements
                    hasPostBox: !!document.querySelector('[data-control-name="share.sharebox_focus"]') ||
                            !!document.querySelector('.share-box-feed-entry__trigger')
                };
                
                // 2. URL-based check
                const urlCheck = {
                    isLoginPage: window.location.href.includes('/login'),
                    isCheckpoint: window.location.href.includes('/checkpoint'),
                    isHomePage: window.location.href.includes('linkedin.com/feed') || 
                                window.location.href === 'https://www.linkedin.com/'
                };
                
                // 3. Login form check
                const loginFormCheck = {
                    hasLoginForm: !!document.querySelector('#username') || 
                                !!document.querySelector('input[name="session_key"]') ||
                                !!document.querySelector('.login__form'),
                    hasSignInButton: !!document.querySelector('a[href="/login"]') ||
                                !!document.querySelector('a[data-tracking-control-name="guest_homepage-basic_sign-in-link"]') ||
                                !!document.querySelector('a.nav__button-secondary')
                };
                
                // 4. Content check
                const contentCheck = {
                    // Check for welcome message text
                    hasWelcomeText: document.body.innerText.includes('Welcome Back') || 
                                document.body.innerText.includes('Good morning') ||
                                document.body.innerText.includes('Good afternoon') ||
                                document.body.innerText.includes('Good evening'),
                    // Check for guest welcome text
                    hasGuestText: document.body.innerText.includes('Join now') &&
                                document.body.innerText.includes('Sign in')
                };
                
                // Count true values in navCheck
                const navValues = Object.values(navCheck);
                const navTrueCount = navValues.filter(Boolean).length;
                
                // Determine login status from multiple criteria
                const isLoggedIn = (
                    // If we have multiple navigation elements present, user is likely logged in
                    (navTrueCount >= 3) &&
                    // And we're not on a login page
                    !urlCheck.isLoginPage && 
                    !urlCheck.isCheckpoint &&
                    // And no login form is visible
                    !loginFormCheck.hasLoginForm
                ) || (
                    // Alternative check: on homepage with welcome text
                    urlCheck.isHomePage && 
                    contentCheck.hasWelcomeText && 
                    !loginFormCheck.hasLoginForm
                );
                
                return {
                    isLoggedIn,
                    details: {
                        navCheck,
                        urlCheck,
                        loginFormCheck,
                        contentCheck,
                        navTrueCount
                    }
                };
            }
            """)
            
            logger.info(f"Login status check result: {login_status.get('isLoggedIn', False)}")
            
            return {
                "isLoggedIn": login_status.get("isLoggedIn", False),
                "message": "User is logged in to LinkedIn" if login_status.get("isLoggedIn", False) else "User is not logged in to LinkedIn",
                "details": login_status.get("details", {})
            }
        except Exception as e:
            logger.exception("Error checking login status")
            return {
                "isLoggedIn": False,
                "error": str(e),
                "message": f"Error checking login status: {str(e)}"
            }
    
    async def _detect_security_challenges(self):
        """Detect security challenges on the page"""
        return await self.page.evaluate("""
        () => {
            // Check for security challenge elements
            const securityElements = [
                // reCAPTCHA elements
                document.querySelector('.recaptcha-checkbox'),
                document.querySelector('.recaptcha-container'),
                document.querySelector('[data-sitekey]'),
                document.querySelector('#captcha'),
                
                // LinkedIn specific security checks
                document.querySelector('#error-for-password'),
                document.querySelector('.security-challenge'),
                document.querySelector('input[name="security_challenge_id"]'),
                document.querySelector('.org-captcha__form'),
                document.querySelector('#challenge-error-page'),
                
                // Security warning messages
                document.querySelector('form.challenge-form'),
                document.querySelector('.authentication-spinner-redirect'),
                document.querySelector('.challenge-dialog')
            ];
            
            // Check page text for security messages
            const pageText = document.body.innerText || '';
            const securityPhrases = [
                'browser or app may not be secure',
                'this browser is not supported',
                'security verification',
                'verify your identity',
                'unusual login activity',
                'we noticed some unusual activity',
                'please verify',
                'security challenge',
                'CAPTCHA',
                'are you a robot',
                'try using a different browser'
            ];
            
            const matchingPhrase = securityPhrases.find(phrase => 
                pageText.toLowerCase().includes(phrase.toLowerCase())
            );
            
            return {
                hasSecurityChallenge: securityElements.some(el => el !== null) || !!matchingPhrase,
                message: matchingPhrase ? 
                    'LinkedIn security alert: "' + matchingPhrase + '"' : 
                    (securityElements.some(el => el !== null) ? 'Security challenge detected' : null),
                currentUrl: window.location.href
            };
        }
        """)
    
    async def _prompt_login(self):
        """Prompt user to log in to LinkedIn"""
        logger.info("Prompting user to log in to LinkedIn")
        
        try:
            # First check if already logged in
            login_status = await self._check_login_status()
            if login_status.get("isLoggedIn", False):
                logger.info("User is already logged in to LinkedIn")
                return {
                    "success": True,
                    "message": "Already logged in to LinkedIn"
                }
            
            # Navigate to LinkedIn login page
            await self.page.goto(
                url="https://www.linkedin.com/login",
                wait_until="domcontentloaded",
                timeout=15000
            )
            
            # Wait for page to load
            await self._wait_for_human_delay(3000, 5000)
            
            # Check for security challenges
            security_check = await self._detect_security_challenges()
            if security_check.get("hasSecurityChallenge", False):
                logger.warning(f"Security challenge detected: {security_check.get('message', '')}")
                return {
                    "success": False,
                    "error": "security_challenge",
                    "message": security_check.get('message', 'Security challenge detected')
                }
            
            # Wait for user to log in (monitor login status)
            max_wait_time = 3 * 60  # 3 minutes
            check_interval = 5  # 5 seconds
            
            logger.info(f"Waiting for user to log in (timeout: {max_wait_time} seconds)")
            
            for _ in range(max_wait_time // check_interval):
                # Wait for check interval
                await asyncio.sleep(check_interval)
                
                # Check login status
                login_status = await self._check_login_status()
                
                # If logged in, return success
                if login_status.get("isLoggedIn", False):
                    logger.info("User successfully logged in to LinkedIn")
                    return {
                        "success": True,
                        "message": "Successfully logged in to LinkedIn"
                    }
                
                # Check for security challenges
                security_check = await self._detect_security_challenges()
                if security_check.get("hasSecurityChallenge", False):
                    logger.warning(f"Security challenge detected during login wait: {security_check.get('message', '')}")
                    # Continue waiting - allow user to complete challenge manually
            
            # If still not logged in after max wait time, return failure
            logger.warning("Login timed out")
            return {
                "success": False,
                "message": "Login timed out after 3 minutes. Please try again."
            }
        except Exception as e:
            logger.exception("Error prompting login")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error prompting login: {str(e)}"
            }
    
    async def _post_to_linkedin(self, text, media_files=None):
        """Post to LinkedIn"""
        logger.info("Posting to LinkedIn")
        
        if media_files is None:
            media_files = []
        
        try:
            # Navigate to LinkedIn feed with a less strict wait condition and longer timeout
            logger.info("Navigating to LinkedIn feed")
            try:
                await self.page.goto(
                    url="https://www.linkedin.com/feed/", 
                    wait_until="load",  # Changed from "networkidle" to "load"
                    timeout=30000  # Increased timeout to 30 seconds
                )
            except Exception as e:
                logger.warning(f"Initial navigation timed out: {e}. Trying with domcontentloaded...")
                # Retry with an even less strict condition
                await self.page.goto(
                    url="https://www.linkedin.com/feed/", 
                    wait_until="domcontentloaded",
                    timeout=20000
                )
            
            # Wait for page to load properly with explicit wait
            logger.info("Waiting for LinkedIn feed to load")
            await asyncio.sleep(5)  # Increased sleep time
            
            # Explicit wait for key feed elements to confirm page load
            try:
                await self.page.wait_for_selector(".feed-shared-update-v2, .share-box-feed-entry__trigger", 
                                                timeout=10000)
                logger.info("LinkedIn feed elements detected")
            except Exception as e:
                logger.warning(f"Could not detect feed elements: {e}")
                # Continue anyway as the elements might still be there
            
            # Save page state for debugging if needed
            debug_dir = os.path.join(os.path.expanduser("~"), "auto_linkedin_debug")
            os.makedirs(debug_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            try:
                # Take a screenshot before attempting to post
                screenshot_path = os.path.join(debug_dir, f"linkedin_feed_{timestamp}.png")
                await self.page.screenshot(path=screenshot_path)
                logger.info(f"Saved debug screenshot to {screenshot_path}")
            except Exception as e:
                logger.warning(f"Failed to save debug screenshot: {str(e)}")
            
            # Try to click the "Start a post" button using the exact structure from the HTML
            logger.info("Looking for 'Start a post' button with precise selectors")
            
            # Create a list of selectors based on the actual HTML structure
            post_button_selectors = [
                "button.artdeco-button.artdeco-button--muted.artdeco-button--4.artdeco-button--tertiary", # Main selector based on classes
                "button.artdeco-button--tertiary span.artdeco-button__text strong", # Target the text inside
                "button.artdeco-button--tertiary span strong", # Simplified version
                "button.share-box-feed-entry__trigger", # Older selector
                ".share-box-feed-entry__top-bar button", # Parent container approach
                "#ember950", # Direct ID (might change but worth trying)
                "button[aria-label='Start a post']", # Try aria-label
                "button.UdjLePnPAvutdJbOgdNCDEfZQcoXOuniyY", # Unique class from HTML
                "button.artdeco-button--muted span strong", # Another approach
                ".share-box-feed-entry__top-bar button.artdeco-button" # Combined approach
            ]
            
            post_button_clicked = False
            
            # Try clicking the button with a more reliable approach first
            try:
                # Click on the element with the text "Start a post" using Playwright's built-in text selector
                await self.page.click('text="Start a post"', timeout=5000)
                post_button_clicked = True
                logger.info("Clicked on 'Start a post' text element")
            except Exception as e:
                logger.debug(f"Could not click on text element: {e}")
            
            # If text click fails, try the selectors
            if not post_button_clicked:
                for selector in post_button_selectors:
                    try:
                        # Check if the element exists and is visible
                        is_visible = await self.page.evaluate(f"""
                        () => {{
                            const el = document.querySelector('{selector}');
                            return el && el.offsetParent !== null;
                        }}
                        """)
                        
                        if is_visible:
                            await self.page.click(selector, timeout=5000)
                            post_button_clicked = True
                            logger.info(f"Clicked post button with selector: {selector}")
                            break
                    except Exception as e:
                        logger.debug(f"Failed to click selector {selector}: {str(e)}")
                        continue
            
            # Try JavaScript approach as a last resort
            if not post_button_clicked:
                logger.info("Trying JavaScript approach to find and click 'Start a post' button")
                try:
                    post_button_clicked = await self.page.evaluate("""
                    () => {
                        // Find buttons that might be the post button
                        const buttons = Array.from(document.querySelectorAll('button'));
                        
                        // Look for strong elements containing "Start a post"
                        for (const button of buttons) {
                            const strongElement = button.querySelector('strong');
                            if (strongElement && strongElement.textContent.trim() === 'Start a post') {
                                button.click();
                                console.log('Found and clicked button with Start a post text');
                                return true;
                            }
                            
                            // Or check if the button text contains "Start a post"
                            if (button.textContent.includes('Start a post')) {
                                button.click();
                                console.log('Found and clicked button with Start a post in text');
                                return true;
                            }
                        }
                        return false;
                    }
                    """)
                except Exception as e:
                    logger.warning(f"JavaScript approach failed: {str(e)}")
            
            if not post_button_clicked:
                logger.error("Could not find 'Start a post' button")
                return {
                    "success": False,
                    "message": "Could not find 'Start a post' button. LinkedIn may have updated their interface."
                }
            
            # Wait for post composer to appear
            logger.info("Waiting for post composer")
            
            try:
                await self.page.wait_for_selector("div.share-box-update", timeout=10000)
            except Exception:
                try:
                    await self.page.wait_for_selector("div[role='dialog'] div[role='textbox']", timeout=10000)
                except Exception:
                    # Try other compositor selectors
                    try:
                        await self.page.wait_for_selector("div.ql-editor", timeout=10000)
                    except Exception as e:
                        logger.error(f"Could not find post composer: {str(e)}")
                        # Take a screenshot to understand what happened
                        try:
                            screenshot_path = os.path.join(debug_dir, f"composer_not_found_{timestamp}.png")
                            await self.page.screenshot(path=screenshot_path)
                            logger.info(f"Saved screenshot when composer not found: {screenshot_path}")
                        except Exception:
                            pass
                            
                        return {
                            "success": False,
                            "message": "Could not find post composer. Please try again."
                        }
            
            # Wait for a moment for the post composer to be fully loaded
            await asyncio.sleep(2)
            
            # Find and focus text input field
            logger.info("Finding text input field")
            
            text_input_selectors = [
                "div[role='textbox']",
                ".editor-content div[contenteditable='true']",
                "div[aria-label='Text editor for creating content']",
                "div.ql-editor",
                ".share-box-update div[contenteditable='true']"
            ]
            
            text_input_element = None
            for selector in text_input_selectors:
                try:
                    text_input_element = await self.page.wait_for_selector(selector, timeout=5000)
                    if text_input_element:
                        logger.info(f"Found text input with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not text_input_element:
                # Try JavaScript to find the input field as a last resort
                try:
                    text_input_found = await self.page.evaluate("""
                    () => {
                        // Find all contenteditable divs
                        const editableDivs = Array.from(document.querySelectorAll('div[contenteditable="true"]'));
                        if (editableDivs.length > 0) {
                            // Focus on the first one
                            editableDivs[0].focus();
                            return true;
                        }
                        return false;
                    }
                    """)
                    
                    if not text_input_found:
                        logger.error("Could not find text input field")
                        return {
                            "success": False,
                            "message": "Could not find text input field. Please try again."
                        }
                except Exception as e:
                    logger.error(f"JavaScript approach to find text input failed: {str(e)}")
                    return {
                        "success": False,
                        "message": "Could not find text input field. Please try again."
                    }
            else:
                # Focus the text input field
                await text_input_element.focus()
            
            # Clear any existing text
            await self.page.keyboard.press("Control+A")
            await self.page.keyboard.press("Backspace")
            
            # Type the post content
            logger.info("Typing post content")
            await self.page.keyboard.type(text=text, delay=50)
            
            # Wait briefly to ensure all text is entered
            await asyncio.sleep(1)
            
            # Upload media files if present
            if media_files:
                logger.info(f"Uploading {len(media_files)} media files")
                
                # First, we need to click the media upload button to reveal the file input
                media_button_selectors = [
                    "button[aria-label='Add a photo']",
                    "button.image-detour-btn",
                    "button[aria-label='Add media']",
                    "button[aria-label='Add image']",
                    ".share-box-feed-entry-toolbar__item button:first-child",
                    "button:has-text('Add media')",
                    "button.share-creation-entry__bottom-row-content-item:first-child"
                ]
                
                media_button_clicked = False
                for selector in media_button_selectors:
                    try:
                        logger.info(f"Trying to click media button with selector: {selector}")
                        await self.page.click(selector, timeout=5000)
                        media_button_clicked = True
                        logger.info(f"Successfully clicked media button with selector: {selector}")
                        break
                    except Exception as e:
                        logger.debug(f"Failed to click media selector {selector}: {str(e)}")
                        continue
                
                if not media_button_clicked:
                    # Try JavaScript approach to find and click the media button
                    try:
                        logger.info("Trying JavaScript approach to find and click media button")
                        media_button_clicked = await self.page.evaluate("""
                        () => {
                            // Try to find buttons with specific text or icons
                            const buttons = Array.from(document.querySelectorAll('button'));
                            
                            // Look for buttons with media-related text or attributes
                            for (const button of buttons) {
                                const buttonText = button.textContent.toLowerCase();
                                const hasPhotoIcon = button.querySelector('svg') !== null;
                                
                                if (buttonText.includes('photo') || 
                                    buttonText.includes('media') || 
                                    buttonText.includes('image') ||
                                    button.getAttribute('aria-label')?.toLowerCase().includes('photo') ||
                                    button.getAttribute('aria-label')?.toLowerCase().includes('media') ||
                                    hasPhotoIcon) {
                                    
                                    console.log('Found media button through JS and clicking it');
                                    button.click();
                                    return true;
                                }
                            }
                            
                            return false;
                        }
                        """)
                        
                        if media_button_clicked:
                            logger.info("Successfully clicked media button using JavaScript")
                    except Exception as e:
                        logger.warning(f"JavaScript approach to click media button failed: {str(e)}")
                
                if media_button_clicked:
                    # Now wait for file input to appear after clicking the media button
                    try:
                        logger.info("Waiting for file input to appear after clicking media button...")
                        await asyncio.sleep(2)  # Give the UI time to update
                        
                        # Try to find the file input that should now be visible or accessible
                        file_input = await self.page.wait_for_selector('input[type="file"]', timeout=8000)
                        
                        if file_input:
                            logger.info("File input found, setting files")
                            await file_input.set_input_files(media_files)
                            logger.info("Files set to input")
                            
                            # Wait for upload to complete with increased timeout
                            await asyncio.sleep(3)  # Give time for upload to process
                            
                            # Check if we can find any upload confirmation elements
                            upload_confirmed = False
                            try:
                                upload_indicator = await self.page.wait_for_selector(
                                    ".share-images__image-loaded, img[alt='Attached image'], .image-selector__image, .share-images, div[role='dialog'] img", 
                                    timeout=15000
                                )
                                if upload_indicator:
                                    logger.info("Media upload confirmed - found upload indicator elements")
                                    upload_confirmed = True
                            except Exception as e:
                                logger.warning(f"Could not find standard upload indicators: {str(e)}")
                                
                                # Try another approach to detect images
                                try:
                                    has_images = await self.page.evaluate("""
                                    () => {
                                        // Look for any images in the composer dialog
                                        const images = document.querySelectorAll('div[role="dialog"] img');
                                        return images.length > 0;
                                    }
                                    """)
                                    
                                    if has_images:
                                        logger.info("Media upload confirmed - found images in dialog")
                                        upload_confirmed = True
                                except Exception:
                                    pass
                            
                            # Take a screenshot to see what happened
                            try:
                                screenshot_path = os.path.join(debug_dir, f"after_media_upload_{timestamp}.png")
                                await self.page.screenshot(path=screenshot_path)
                                logger.info(f"Saved screenshot after media upload: {screenshot_path}")
                            except Exception as e:
                                logger.warning(f"Could not save screenshot: {str(e)}")

                            # If upload is confirmed, try to click the Next button in the media editor dialog
                            if upload_confirmed:
                                logger.info("Attempting to click 'Next' button in media editor dialog")
                                
                                # Try using specific selectors for the Next button
                                next_button_selectors = [
                                    "button.share-box-footer__primary-btn",  # Most reliable class-based selector
                                    "button[aria-label='Next']",  # Aria label is usually stable
                                    "div.share-box-footer__main-actions button.artdeco-button--primary",  # More specific parent-based selector
                                    "div.share-box-footer button:nth-child(2)",  # Position-based selector (usually second button)
                                    "button.artdeco-button--primary:has-text('Next')",  
                                    "div.share-box-footer button:has-text('Next')",
                                    "#ember484",  # Try the ID from the latest example
                                    "#ember593"   # Original ID as last resort
                                ]
                                
                                next_button_clicked = False
                                for selector in next_button_selectors:
                                    try:
                                        logger.info(f"Trying to click Next button with selector: {selector}")
                                        await self.page.click(selector, timeout=5000)
                                        next_button_clicked = True
                                        logger.info(f"Successfully clicked Next button with selector: {selector}")
                                        # Wait a moment for the UI to update after clicking Next
                                        await asyncio.sleep(2)
                                        break
                                    except Exception as e:
                                        logger.debug(f"Failed to click Next button selector {selector}: {str(e)}")
                                        continue
                                
                                # If standard selectors didn't work, try a more robust JavaScript approach
                                if not next_button_clicked:
                                    try:
                                        logger.info("Trying enhanced JavaScript approach to find and click Next button")
                                        next_button_clicked = await self.page.evaluate("""
                                        () => {
                                            // First try the most specific approach - look in the footer
                                            const footer = document.querySelector('.share-box-footer');
                                            if (footer) {
                                                console.log('Found share-box-footer');
                                                // Look for the primary button in main actions
                                                const mainActions = footer.querySelector('.share-box-footer__main-actions');
                                                if (mainActions) {
                                                    console.log('Found main actions');
                                                    // Try to find the primary button (usually the second one, or the one with primary class)
                                                    const buttons = mainActions.querySelectorAll('button');
                                                    let nextButton = null;
                                                    
                                                    // Find button by position (usually the second one is Next)
                                                    if (buttons.length >= 2) {
                                                        nextButton = buttons[1]; // Second button is usually Next
                                                        console.log('Found Next button by position (second button)');
                                                    }
                                                    
                                                    // Or find by class
                                                    if (!nextButton) {
                                                        nextButton = mainActions.querySelector('.artdeco-button--primary');
                                                        if (nextButton) console.log('Found Next button by primary class');
                                                    }
                                                    
                                                    if (nextButton) {
                                                        nextButton.click();
                                                        return true;
                                                    }
                                                }
                                                
                                                // Try directly on the footer if main actions not found
                                                const primaryBtn = footer.querySelector('.share-box-footer__primary-btn, button.artdeco-button--primary');
                                                if (primaryBtn) {
                                                    console.log('Found primary button in footer');
                                                    primaryBtn.click();
                                                    return true;
                                                }
                                            }
                                            
                                            // Try a general approach searching all buttons
                                            const buttons = Array.from(document.querySelectorAll('button'));
                                            
                                            // Look for buttons with Next text or aria-label
                                            for (const button of buttons) {
                                                const buttonText = button.textContent.trim().toLowerCase();
                                                const ariaLabel = button.getAttribute('aria-label')?.toLowerCase() || '';
                                                
                                                if (buttonText.includes('next') || ariaLabel === 'next') {
                                                    console.log('Found Next button by text/aria-label');
                                                    button.click();
                                                    return true;
                                                }
                                                
                                                // Also check for class-based identification
                                                if (button.classList.contains('share-box-footer__primary-btn') || 
                                                    (button.classList.contains('artdeco-button--primary') && 
                                                     button.closest('.share-box-footer'))) {
                                                    console.log('Found Next button by class');
                                                    button.click();
                                                    return true;
                                                }
                                            }
                                            
                                            // One last attempt - try to find by relative positioning
                                            // Look for a Back button, then get its next sibling
                                            const backButton = Array.from(document.querySelectorAll('button')).find(b => 
                                                b.textContent.trim().toLowerCase() === 'back' || 
                                                b.getAttribute('aria-label')?.toLowerCase() === 'back'
                                            );
                                            
                                            if (backButton && backButton.parentElement) {
                                                const siblings = Array.from(backButton.parentElement.children);
                                                const backIndex = siblings.indexOf(backButton);
                                                if (backIndex >= 0 && backIndex < siblings.length - 1) {
                                                    const nextButton = siblings[backIndex + 1];
                                                    if (nextButton.tagName.toLowerCase() === 'button') {
                                                        console.log('Found Next button by relation to Back button');
                                                        nextButton.click();
                                                        return true;
                                                    }
                                                }
                                            }
                                            
                                            // Could not find the Next button
                                            return false;
                                        }
                                        """)
                                        
                                        if next_button_clicked:
                                            logger.info("Successfully clicked Next button using enhanced JavaScript approach")
                                            await asyncio.sleep(2)
                                    except Exception as e:
                                        logger.warning(f"Enhanced JavaScript approach to click Next button failed: {str(e)}")
                                
                                if not next_button_clicked:
                                    # As a last resort, try to use a more direct approach by coordinates or simulating Enter
                                    try:
                                        logger.info("Trying to use direct methods to proceed")
                                        
                                        # First try with Enter key (sometimes this advances the flow)
                                        await self.page.keyboard.press("Enter")
                                        logger.info("Pressed Enter key as fallback")
                                        await asyncio.sleep(2)
                                        
                                        # Take a screenshot to see what happened
                                        try:
                                            screenshot_path = os.path.join(debug_dir, f"after_enter_key_{timestamp}.png")
                                            await self.page.screenshot(path=screenshot_path)
                                            logger.info(f"Saved screenshot after pressing Enter: {screenshot_path}")
                                        except Exception:
                                            pass
                                        
                                        # Check if we've moved to the next screen by looking for the Post button
                                        post_button_check = await self.page.query_selector("button.share-actions__primary-action, button:has-text('Post')")
                                        if post_button_check:
                                            logger.info("Successfully moved to post screen after pressing Enter")
                                            next_button_clicked = True
                                    except Exception as e:
                                        logger.warning(f"Direct methods failed: {str(e)}")
                                
                                if not next_button_clicked:
                                    logger.warning("Could not find or click the Next button in media editor dialog")
                                    # Take a screenshot to see what happened
                                    try:
                                        screenshot_path = os.path.join(debug_dir, f"next_button_not_found_{timestamp}.png")
                                        await self.page.screenshot(path=screenshot_path)
                                        logger.info(f"Saved screenshot when Next button not found: {screenshot_path}")
                                    except Exception:
                                        pass
                                
                            # Check for any open file dialogs and dismiss them if any
                            try:
                                # Look for cancel buttons in dialogs
                                cancel_buttons = await self.page.query_selector_all("button[aria-label='Cancel'], button:has-text('Cancel')")
                                if len(cancel_buttons) > 0:
                                    logger.info("Found cancel button in dialog, clicking to dismiss")
                                    await cancel_buttons[0].click()
                            except Exception as e:
                                logger.warning(f"Error checking for dialog: {str(e)}")
                                
                            # Only press Escape to dismiss dialogs if we didn't successfully click the Next button
                            # or if upload was not confirmed
                            if not upload_confirmed or (upload_confirmed and not next_button_clicked):
                                # Press Escape to dismiss any open dialogs as a last resort
                                await self.page.keyboard.press("Escape")
                                logger.info("Pressed Escape to dismiss any potential open dialogs")
                                await asyncio.sleep(1)
                        else:
                            logger.error("Could not find file input element after clicking media button")
                    except Exception as e:
                        logger.error(f"Error during media upload process: {str(e)}")
                        # Press Escape to dismiss any dialogs and continue
                        await self.page.keyboard.press("Escape")
                        logger.info("Pressed Escape to dismiss any potential dialogs")
                else:
                    logger.warning("Could not find or click the media upload button, skipping media upload")
            
            # Wait before posting with a longer delay to ensure everything is ready
            await asyncio.sleep(3)
            
            # Click the "Post" button
            logger.info("Clicking 'Post' button")
            
            post_submit_selectors = [
                "#ember629",  # Specific ID from the HTML
                "button.share-actions__primary-action",
                ".share-box_actions button",  # Container selector from HTML
                "button.share-actions__primary-action.artdeco-button--primary",
                "button:has-text('Post')",
                "button[aria-label='Post']",
                ".share-box_actions button[type='submit']",
                "div[role='dialog'] button.artdeco-button--primary"
            ]
            
            post_submit_clicked = False
            for selector in post_submit_selectors:
                try:
                    logger.info(f"Trying to click Post button with selector: {selector}")
                    await self.page.click(selector, timeout=5000)
                    post_submit_clicked = True
                    logger.info(f"Clicked submit button with selector: {selector}")
                    break
                except Exception as e:
                    logger.debug(f"Failed to click Post button selector {selector}: {str(e)}")
                    continue
            
            if not post_submit_clicked:
                # Try using JavaScript to find and click the Post button
                try:
                    logger.info("Trying JavaScript approach to find and click Post button")
                    post_submit_clicked = await self.page.evaluate("""
                    () => {
                        // First try to find by specific container and class structure from the HTML
                        const shareBoxActions = document.querySelector('.share-box_actions');
                        if (shareBoxActions) {
                            const postButton = shareBoxActions.querySelector('button');
                            if (postButton) {
                                console.log('Found post button in share-box_actions container');
                                postButton.click();
                                return true;
                            }
                        }
                        
                        // Try to find by specific container
                        const footerContainer = document.querySelector('.share-creation-state__footer');
                        if (footerContainer) {
                            const postButton = footerContainer.querySelector('button:not(.share-actions__scheduled-post-btn)');
                            if (postButton && postButton.textContent.trim().toLowerCase() === 'post') {
                                console.log('Found post button in share-creation-state__footer container');
                                postButton.click();
                                return true;
                            }
                        }
                        
                        // Find all buttons
                        const buttons = Array.from(document.querySelectorAll('button'));
                        
                        // Look for the Post button by text
                        const postButton = buttons.find(b => 
                            b.textContent.trim() === 'Post' || 
                            b.textContent.includes('Post')
                        );
                        
                        if (postButton) {
                            console.log('Found post button by text content');
                            postButton.click();
                            return true;
                        }
                        
                        // Look for primary button (usually the submit)
                        const primaryButton = buttons.find(b => 
                            b.classList.contains('artdeco-button--primary') && 
                            b.classList.contains('share-actions__primary-action')
                        );
                        
                        if (primaryButton) {
                            console.log('Found post button by primary action class');
                            primaryButton.click();
                            return true;
                        }
                        
                        // Try by ID if available
                        const emberButton = document.querySelector('#ember629');
                        if (emberButton) {
                            console.log('Found post button by specific ID');
                            emberButton.click();
                            return true;
                        }
                        
                        return false;
                    }
                    """)
                    
                    if post_submit_clicked:
                        logger.info("Clicked Post button with JavaScript")
                except Exception as e:
                    logger.error(f"JavaScript approach for Post button failed: {str(e)}")
            
            if not post_submit_clicked:
                logger.error("Could not find 'Post' button")
                
                # Take a screenshot to help with debugging
                try:
                    screenshot_path = os.path.join(debug_dir, f"post_button_not_found_{timestamp}.png")
                    await self.page.screenshot(path=screenshot_path)
                    logger.info(f"Saved screenshot when Post button not found: {screenshot_path}")
                except Exception as e:
                    logger.warning(f"Could not save debug screenshot: {str(e)}")
                
                # Try to get HTML structure to help with future debugging
                try:
                    html_structure = await self.page.evaluate("""
                    () => {
                        const getStructure = (element, depth = 0) => {
                            if (!element) return '';
                            const indent = ' '.repeat(depth * 2);
                            let result = indent + element.tagName.toLowerCase();
                            
                            if (element.id) result += `#${element.id}`;
                            if (element.className) {
                                const classes = element.className.toString().split(/\\s+/).filter(c => c);
                                if (classes.length) result += `.${classes.join('.')}`;
                            }
                            
                            // Add button text if this is a button
                            if (element.tagName.toLowerCase() === 'button') {
                                result += ` [text: "${element.textContent.trim()}"]`;
                            }
                            
                            result += '\\n';
                            
                            // Get children structure
                            for (const child of element.children) {
                                result += getStructure(child, depth + 1);
                            }
                            
                            return result;
                        };
                        
                        // Look for important containers
                        const containers = [
                            document.querySelector('.share-creation-state__footer'),
                            document.querySelector('.share-box_actions'),
                            document.querySelector('div[role="dialog"]')
                        ].filter(Boolean);
                        
                        return containers.map(c => getStructure(c)).join('\\n');
                    }
                    """)
                    
                    logger.info(f"HTML structure for debugging:\n{html_structure}")
                except Exception as e:
                    logger.warning(f"Could not get HTML structure for debugging: {str(e)}")
                
                return {
                    "success": False,
                    "message": "Could not find the 'Post' button to submit your post."
                }
            
            # Wait for post to be submitted and feed to update
            logger.info("Waiting for post to be submitted")
            await asyncio.sleep(5)
            
            # Check for any lingering dialogs and close them
            logger.info("Checking for any lingering dialogs after posting")
            try:
                # First attempt: Look for dialog close buttons
                close_button_selectors = [
                    "button[aria-label='Close']", 
                    "button[aria-label='Dismiss']",
                    "button.artdeco-modal__dismiss",
                    ".artdeco-modal__dismiss",
                    "button.share-box-footer__close-btn",
                    "button:has-text('Done')",
                    "button:has-text('Close')"
                ]
                
                for selector in close_button_selectors:
                    try:
                        close_buttons = await self.page.query_selector_all(selector)
                        if close_buttons and len(close_buttons) > 0:
                            logger.info(f"Found {len(close_buttons)} dialog close buttons with selector: {selector}")
                            # Click each close button found
                            for button in close_buttons:
                                await button.click()
                                logger.info(f"Clicked dialog close button")
                                await asyncio.sleep(1)
                            break
                    except Exception as e:
                        logger.debug(f"No close button found with selector {selector} or error clicking: {str(e)}")
                
                # Second attempt: Try JavaScript to find and close dialogs more comprehensively
                lingering_dialogs = await self.page.evaluate("""
                () => {
                    // Look for any dialogs and modals across the page
                    const dialogs = document.querySelectorAll('div[role="dialog"]');
                    const modalBackdrops = document.querySelectorAll('.artdeco-modal-overlay');
                    const mediaDialogs = document.querySelectorAll('.share-images, .share-creation-state');
                    
                    // Keep track of what was found and closed
                    let closed = false;
                    const results = {
                        dialogsFound: dialogs.length,
                        modalBackdropsFound: modalBackdrops.length,
                        mediaDialogsFound: mediaDialogs.length,
                        buttonsClosed: []
                    };
                    
                    // Various ways to close dialogs
                    const closeDialog = (element) => {
                        // Try to find close buttons with different patterns
                        const closeSelectors = [
                            'button[aria-label="Close"]', 
                            'button[aria-label="Dismiss"]',
                            'button.artdeco-modal__dismiss',
                            '.artdeco-modal__dismiss',
                            'button.share-box-footer__close-btn',
                            'button:has-text("Done")',
                            'button:has-text("Close")',
                            '.share-box-footer__close-btn'
                        ];
                        
                        // Check each selector
                        for (const selector of closeSelectors) {
                            try {
                                const closeButton = element.querySelector(selector);
                                if (closeButton) {
                                    closeButton.click();
                                    results.buttonsClosed.push(selector);
                                    closed = true;
                                    return true;
                                }
                            } catch (e) {
                                console.error('Error trying selector', selector, e);
                            }
                        }
                        
                        // Try finding buttons with text or aria-label containing "close", "dismiss", "done"
                        const buttons = element.querySelectorAll('button');
                        for (const button of buttons) {
                            const text = (button.textContent || '').toLowerCase().trim();
                            const ariaLabel = (button.getAttribute('aria-label') || '').toLowerCase();
                            
                            if (text.includes('close') || text.includes('dismiss') || text.includes('done') ||
                                ariaLabel.includes('close') || ariaLabel.includes('dismiss') || ariaLabel.includes('done')) {
                                button.click();
                                results.buttonsClosed.push(`button with text: "${text}" or aria-label: "${ariaLabel}"`);
                                closed = true;
                                return true;
                            }
                        }
                        
                        return false;
                    };
                    
                    // Try with all dialog types
                    [...dialogs, ...modalBackdrops, ...mediaDialogs].forEach(dialog => {
                        if (dialog) closeDialog(dialog);
                    });
                    
                    // Try one more approach - look for "Done" or "Close" buttons anywhere
                    if (!closed) {
                        const anyCloseButton = document.querySelector('button:has-text("Done"), button:has-text("Close"), button[aria-label="Close"]');
                        if (anyCloseButton) {
                            anyCloseButton.click();
                            results.buttonsClosed.push('Found global close button');
                            closed = true;
                        }
                    }
                    
                    results.closed = closed;
                    return results;
                }
                """)
                
                if lingering_dialogs:
                    logger.info(f"Dialog check results: {lingering_dialogs}")
                    
                    # If we found dialogs but couldn't close them with buttons, try a series of fallbacks
                    if (lingering_dialogs.get('dialogsFound', 0) > 0 or 
                        lingering_dialogs.get('modalBackdropsFound', 0) > 0 or
                        lingering_dialogs.get('mediaDialogsFound', 0) > 0) and not lingering_dialogs.get('closed', False):
                        
                        # Try clicking elsewhere on the page to dismiss overlays
                        logger.info("Trying to click on the background to dismiss dialogs")
                        try:
                            # Click on a safe area (top of page near LinkedIn logo)
                            await self.page.mouse.click(50, 50)
                            await asyncio.sleep(1)
                        except Exception as e:
                            logger.debug(f"Background click failed: {str(e)}")
                        
                        # Try pressing Escape key twice with delay
                        logger.info("Found lingering dialogs, pressing Escape to close")
                        await self.page.keyboard.press("Escape")
                        await asyncio.sleep(1)
                        
                        # Press Escape again 
                        await self.page.keyboard.press("Escape")
                        await asyncio.sleep(1)
                        
                        # As a last resort, try tab + enter (focus on a close button and activate it)
                        logger.info("Trying tab + enter to find and activate close buttons")
                        for _ in range(5):  # Try up to 5 tabs to find a close button
                            await self.page.keyboard.press("Tab")
                            await asyncio.sleep(0.3)
                        await self.page.keyboard.press("Enter")
                        await asyncio.sleep(1)
                        
                # Take a final screenshot to verify state after attempting to close dialogs
                try:
                    screenshot_path = os.path.join(debug_dir, f"after_dialog_closing_{timestamp}.png")
                    await self.page.screenshot(path=screenshot_path)
                    logger.info(f"Saved final screenshot after dialog closing attempts: {screenshot_path}")
                except Exception as e:
                    logger.warning(f"Could not save final debug screenshot: {str(e)}")
                
            except Exception as e:
                logger.warning(f"Error attempting to close dialogs after posting: {str(e)}")
                # This shouldn't affect the overall success of posting
            
            return {
                "success": True,
                "message": "Successfully posted to LinkedIn"
            }
        except Exception as e:
            logger.exception("Error posting to LinkedIn")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error posting to LinkedIn: {str(e)}"
            }
    
    async def _check_success_message(self, element):
        """Check if success message element contains success text"""
        text = await element.text_content()
        return "posted" in text.lower() or "shared" in text.lower() or "success" in text.lower() 