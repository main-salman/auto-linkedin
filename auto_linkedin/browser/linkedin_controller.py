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
            args=[
                "--disable-blink-features=AutomationControlled",
                "--window-size=1280,800"
            ]
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
            # Navigate to LinkedIn feed
            await self.page.goto(
                url="https://www.linkedin.com/feed/", 
                wait_until="domcontentloaded",
                timeout=15000
            )
            
            # Wait for page to load
            await self._wait_for_human_delay(2000, 3000)
            
            # Save page state for debugging if needed
            debug_dir = os.path.join(os.path.expanduser("~"), "auto_linkedin_debug")
            os.makedirs(debug_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            try:
                # Take a screenshot before attempting to post
                screenshot_path = os.path.join(debug_dir, f"linkedin_feed_{timestamp}.png")
                await self.page.screenshot(path=screenshot_path)
                logger.info(f"Saved debug screenshot to {screenshot_path}")
                
                # Save page HTML for debugging
                html_path = os.path.join(debug_dir, f"linkedin_feed_{timestamp}.html")
                html_content = await self.page.content()
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"Saved debug HTML to {html_path}")
            except Exception as e:
                logger.warning(f"Failed to save debug information: {str(e)}")
                
            # Click on "Start a post" button
            logger.info("Clicking on 'Start a post' button")
            
            # First try to navigate to the feed page if not already there
            current_url = await self.page.evaluate("window.location.href")
            if not "linkedin.com/feed" in current_url:
                logger.info("Navigating to LinkedIn feed page")
                await self.page.goto(
                    url="https://www.linkedin.com/feed/",
                    wait_until="domcontentloaded",
                    timeout=15000
                )
                await self._wait_for_human_delay(3000, 5000)
            
            # Try different approaches to click the post button
            
            # 1. First try direct DOM selectors
            post_button_selectors = [
                # Use the exact ID and class structure from the provided HTML
                "#ember36",  # Direct ID selector from the HTML
                "button.artdeco-button.artdeco-button--tertiary", # Class combination from HTML
                "button.artdeco-button strong:contains('Start a post')",
                "button.artdeco-button span span strong",
                "button.artdeco-button--muted.artdeco-button--tertiary",
                "button[id^='ember'] span strong",  # Any ember button with "Start a post" text
                
                # More general selectors as fallback
                ".share-box-feed-entry__trigger", 
                ".share-box-feed-entry__trigger span",
                ".artdeco-text-input--input",
                "[aria-placeholder='Start a post']",
                "[placeholder='Start a post']",
                ".share-box__open .share-box-feed-entry__subtitle",
                ".artdeco-card .share-box-feed-entry",
                ".share-box-feed-entry",
                "button[aria-label='Start a post']",
                "div[aria-label='Start a post']",
                "div[data-control-name='share.sharebox_focus']",
                "div.share-box-feed-entry__trigger",
                "button.artdeco-button[data-control-name='create_post']",
                "div[data-urn='urn:li:control:d_flagship3_feed_share_box']",
                "button.share-box-feed-entry__trigger",
                "button.share-box__open",
                "div.share-box__trigger",
                "button.share-box-media-entry__trigger"
            ]
            
            post_button_clicked = False
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
                    
            # 2. Try finding elements by text content using evaluate
            if not post_button_clicked:
                logger.info("Trying to find and click button with exact text structure")
                try:
                    post_button_clicked = await self.page.evaluate("""
                    () => {
                        // Look for button with exact structure matching LinkedIn's "Start a post" button
                        const buttons = Array.from(document.querySelectorAll('button.artdeco-button'));
                        
                        for (const button of buttons) {
                            // Check for the nested structure
                            const strong = button.querySelector('span span.t-normal strong');
                            if (strong && strong.textContent.trim() === 'Start a post') {
                                button.click();
                                console.log('Found and clicked "Start a post" button with exact structure');
                                return true;
                            }
                        }
                        
                        // Alternative approach - find any button with "Start a post" text
                        for (const button of buttons) {
                            if (button.textContent.includes('Start a post')) {
                                button.click();
                                console.log('Found and clicked button containing "Start a post" text');
                                return true;
                            }
                        }
                        
                        return false;
                    }
                    """)
                    
                    if post_button_clicked:
                        logger.info("Clicked button found by text structure")
                except Exception as e:
                    logger.warning(f"Failed to find button by text structure: {str(e)}")
                    
            # 3. Try clicking the post box using the exact coordinates from the screenshot (fixed position)
            if not post_button_clicked:
                logger.info("Trying to click at fixed position where post box is located")
                try:
                    # Try clicking on the post box at an approximate position based on the screenshot
                    await self.page.mouse.click(650, 300)  # Adjust these coordinates based on the screenshot
                    post_button_clicked = True
                    logger.info("Clicked at fixed position (650, 300)")
                except Exception as e:
                    logger.warning(f"Failed to click at fixed position: {str(e)}")
                    
            # 4. Try to identify buttons by their ID pattern
            if not post_button_clicked:
                logger.info("Trying to find ember buttons that might be the post button")
                try:
                    post_button_clicked = await self.page.evaluate("""
                    () => {
                        // Find all ember buttons (LinkedIn uses ember for many components)
                        const emberButtons = Array.from(document.querySelectorAll('button[id^="ember"]'));
                        console.log('Found', emberButtons.length, 'ember buttons');
                        
                        // Sort buttons by their vertical position (post button is usually at the top)
                        emberButtons.sort((a, b) => {
                            const rectA = a.getBoundingClientRect();
                            const rectB = b.getBoundingClientRect();
                            return rectA.top - rectB.top;
                        });
                        
                        // Try to click buttons that are visible in the top portion
                        for (const button of emberButtons.slice(0, 5)) {
                            const rect = button.getBoundingClientRect();
                            
                            // Check if button is visible and in the top portion of the page
                            if (rect.top > 0 && rect.top < 400 && rect.height > 0 && rect.width > 0) {
                                console.log('Clicking ember button:', button.id, 'at position:', rect.top);
                                button.click();
                                return true;
                            }
                        }
                        
                        return false;
                    }
                    """)
                    
                    if post_button_clicked:
                        logger.info("Clicked ember button in top portion of page")
                except Exception as e:
                    logger.warning(f"Failed to find ember buttons: {str(e)}")
                    
            # 5. Last resort - try taking a screenshot and clicking in the center of the feed
            if not post_button_clicked:
                logger.info("Trying to click directly in the center of the post box area")
                try:
                    # Get page dimensions
                    dimensions = await self.page.evaluate("""
                    () => {
                        return {
                            width: document.documentElement.clientWidth,
                            height: document.documentElement.clientHeight
                        };
                    }
                    """)
                    
                    # Calculate center of the feed area (slightly above center)
                    center_x = dimensions['width'] / 2
                    center_y = (dimensions['height'] / 2) - 100  # Slightly above center
                    
                    # Click at calculated position
                    await self.page.mouse.click(center_x, center_y)
                    post_button_clicked = True
                    logger.info(f"Clicked at center of feed area ({center_x}, {center_y})")
                except Exception as e:
                    logger.warning(f"Failed to click at center: {str(e)}")
            
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
                except Exception as e:
                    logger.error(f"Could not find post composer: {str(e)}")
                    return {
                        "success": False,
                        "message": "Could not find post composer. Please try again."
                    }
            
            # Wait for a moment for the post composer to be fully loaded
            await self._wait_for_human_delay(1000, 2000)
            
            # Find and focus text input field
            logger.info("Finding text input field")
            
            text_input_selectors = [
                "div[role='textbox']",
                ".editor-content div[contenteditable='true']",
                "div[aria-label='Text editor for creating content']",
                "div.ql-editor"
            ]
            
            text_input_element = None
            for selector in text_input_selectors:
                try:
                    text_input_element = await self.page.wait_for_selector(selector, timeout=5000)
                    if text_input_element:
                        break
                except Exception:
                    continue
            
            if not text_input_element:
                logger.error("Could not find text input field")
                return {
                    "success": False,
                    "message": "Could not find text input field. Please try again."
                }
            
            # Focus the text input field
            await text_input_element.focus()
            
            # Clear any existing text
            await self.page.keyboard.press("Control+A")
            await self.page.keyboard.press("Backspace")
            
            # Type the post content (using a more reliable single-string approach)
            logger.info("Typing post content")
            
            # Instead of typing character by character, type the whole text at once
            await self.page.keyboard.type(text=text, delay=50)
            
            # Wait briefly to ensure all text is entered
            await self._wait_for_human_delay(1000, 2000)
            
            # Upload media files if present
            if media_files:
                logger.info(f"Uploading {len(media_files)} media files")
                
                # Click media upload button
                media_button_selectors = [
                    "button[aria-label='Add a photo']",
                    "button[aria-label='Add media']",
                    "button[aria-label='Add image']"
                ]
                
                media_button_clicked = False
                for selector in media_button_selectors:
                    try:
                        await self.page.click(selector, timeout=5000)
                        media_button_clicked = True
                        break
                    except Exception:
                        continue
                
                if not media_button_clicked:
                    logger.warning("Could not find media upload button, trying fallback method")
                    
                    # Fallback: use JavaScript to find and click button
                    media_button_clicked = await self.page.evaluate("""
                    () => {
                        // Find media upload button by text content
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const mediaButton = buttons.find(btn => 
                            btn.textContent.includes('Add media') || 
                            btn.textContent.includes('Add a photo') ||
                            btn.textContent.includes('Photo')
                        );
                        
                        if (mediaButton) {
                            mediaButton.click();
                            return true;
                        }
                        
                        return false;
                    }
                    """)
                
                if not media_button_clicked:
                    logger.warning("Could not find media upload button, continuing without media")
                else:
                    # Wait for file input to be available
                    file_input = await self.page.wait_for_selector("input[type='file']", timeout=5000)
                    
                    if file_input:
                        # Upload files
                        await file_input.set_input_files(media_files)
                        
                        # Wait for upload to complete
                        try:
                            # First check if media is already visible in the post
                            media_visible = await self.page.evaluate("""
                            () => {
                                // Check for various indicators that media is attached
                                const hasAttachedImage = !!document.querySelector('.share-images__image-loaded, img[alt="Attached image"], .image-sharing-attachment, .editor-image');
                                const hasMediaPreview = !!document.querySelector('.editor-media, .editor-content img, .editor-content video');
                                
                                console.log('Media attachment check:', hasAttachedImage, hasMediaPreview);
                                return hasAttachedImage || hasMediaPreview;
                            }
                            """)
                            
                            if not media_visible:
                                # If media not yet visible, wait for it but with a shorter timeout
                                await self.page.wait_for_selector(".share-images__image-loaded, img[alt='Attached image'], .editor-media, .editor-content img", timeout=8000)
                            
                            # Media is now attached, wait for upload to stabilize
                            await self._wait_for_human_delay(2000, 3000)
                            
                            # Take screenshot of the post with media to verify attachment
                            debug_dir = os.path.join(os.path.expanduser("~"), "auto_linkedin_debug")
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            screenshot_path = os.path.join(debug_dir, f"media_attached_{timestamp}.png")
                            await self.page.screenshot(path=screenshot_path)
                            logger.info(f"Saved media attachment screenshot to {screenshot_path}")
                            
                            # Close any open media dialog that might be remaining open
                            # First check if there's an open dialog
                            has_dialog = await self.page.evaluate("""
                            () => {
                                return {
                                    hasDialog: !!document.querySelector('div[role="dialog"]') || !!document.querySelector('.artdeco-modal'),
                                    hasBackdrop: !!document.querySelector('.artdeco-modal-overlay')
                                };
                            }
                            """)
                            
                            if has_dialog.get('hasDialog', False):
                                logger.info("Dialog detected after media upload, attempting to close it")
                                
                                # Try multiple approaches to close the dialog
                                close_button_selectors = [
                                    "button[aria-label='Close']",
                                    "button[aria-label='Cancel']",
                                    "button.media-upload-cancel",
                                    "button.artdeco-modal__dismiss",
                                    ".artdeco-modal__dismiss",
                                    ".artdeco-modal__close"
                                ]
                                
                                # Try clicking close buttons
                                close_clicked = False
                                for selector in close_button_selectors:
                                    try:
                                        close_button = await self.page.query_selector(selector)
                                        if close_button:
                                            await close_button.click()
                                            logger.info(f"Clicked close button with selector: {selector}")
                                            close_clicked = True
                                            await self._wait_for_human_delay(1000, 1500)
                                            break
                                    except Exception as e:
                                        logger.debug(f"Failed to click close button {selector}: {str(e)}")
                                
                                # If no button clicked but we have backdrop, click outside the dialog
                                if not close_clicked and has_dialog.get('hasBackdrop', False):
                                    try:
                                        # Click away from the dialog (top corner)
                                        await self.page.mouse.click(10, 10)
                                        logger.info("Clicked outside dialog to dismiss it")
                                        await self._wait_for_human_delay(1000, 1500)
                                    except Exception as e:
                                        logger.debug(f"Failed to click outside dialog: {str(e)}")
                                
                                # If still not closed, try pressing Escape
                                has_dialog_after_clicks = await self.page.evaluate("""
                                () => {
                                    return !!document.querySelector('div[role="dialog"]') || 
                                           !!document.querySelector('.artdeco-modal');
                                }
                                """)
                                
                                if has_dialog_after_clicks:
                                    logger.info("Dialog still detected, pressing Escape")
                                    await self.page.keyboard.press("Escape")
                                    await self._wait_for_human_delay(1000, 1500)
                                    
                                    # Verify dialog closed after Escape
                                    has_dialog_after_escape = await self.page.evaluate("""
                                    () => {
                                        return !!document.querySelector('div[role="dialog"]') || 
                                               !!document.querySelector('.artdeco-modal');
                                    }
                                    """)
                                    
                                    if has_dialog_after_escape:
                                        logger.warning("Dialog still open after multiple close attempts")
                                        # Continue anyway, the media might still be attached
                                
                        except Exception as e:
                            logger.warning(f"Could not confirm media upload completion: {str(e)}")
                            # Check if media is visible despite the error
                            try:
                                media_visible = await self.page.evaluate("""
                                () => {
                                    return !!document.querySelector('.share-images__image-loaded, img[alt="Attached image"], .editor-media, .editor-content img, .editor-content video');
                                }
                                """)
                                
                                if media_visible:
                                    logger.info("Media appears to be attached despite confirmation error")
                                else:
                                    logger.warning("Media may not be attached to the post")
                            except Exception:
                                pass
                            # Continue anyway
            
            # Wait before posting
            await self._wait_for_human_delay(1000, 2000)
            
            # Click the "Post" button
            logger.info("Clicking 'Post' button")
            
            post_submit_selectors = [
                "button:has-text('Post')",
                "button[aria-label='Post']",
                "button.share-actions__primary-action",
                "button.share-box_actions__primary-action",
                "button[data-control-name='share.post']",
                "button.share-actions__publish-button",
                "div[data-control-name='share.post']",
                "button.post-button",
                "button.artdeco-button--primary"
            ]
            
            # Take a screenshot before attempting to find Post button
            debug_dir = os.path.join(os.path.expanduser("~"), "auto_linkedin_debug")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(debug_dir, f"before_post_button_{timestamp}.png")
            await self.page.screenshot(path=screenshot_path)
            logger.info(f"Saved screenshot before clicking Post button: {screenshot_path}")
            
            # First, try to find all buttons in the composer footer
            try:
                composer_buttons = await self.page.evaluate("""
                () => {
                    // Get all buttons in the UI
                    const allButtons = Array.from(document.querySelectorAll('button'));
                    
                    // Log information about potential post buttons to help with debugging
                    const buttonInfo = allButtons
                        .filter(btn => btn.offsetParent !== null) // Only visible buttons
                        .map(btn => ({
                            text: btn.textContent.trim(),
                            classes: btn.className,
                            id: btn.id,
                            type: btn.type,
                            ariaLabel: btn.getAttribute('aria-label'),
                            isPrimary: btn.className.includes('primary'),
                            rect: btn.getBoundingClientRect()
                        }));
                    
                    console.log('Found buttons:', JSON.stringify(buttonInfo));
                    
                    // Return array of visible buttons with 'Post' text
                    const postButtons = allButtons.filter(btn => 
                        btn.offsetParent !== null && 
                        (btn.textContent.trim() === 'Post' || 
                         btn.getAttribute('aria-label') === 'Post')
                    );
                    
                    if (postButtons.length > 0) {
                        postButtons[0].click();
                        console.log('Clicked post button with text:', postButtons[0].textContent);
                        return true;
                    }
                    
                    return false;
                }
                """)
                
                if composer_buttons:
                    post_submit_clicked = True
                    logger.info("Clicked Post button found with JavaScript")
            except Exception as e:
                logger.debug(f"Error finding composer buttons: {str(e)}")
            
            # Try standard selectors if JavaScript approach didn't work
            if not post_submit_clicked:
                for selector in post_submit_selectors:
                    try:
                        await self.page.click(selector, timeout=5000)
                        post_submit_clicked = True
                        logger.info(f"Clicked submit button with selector: {selector}")
                        break
                    except Exception:
                        continue
            
            # Try looking for primary (usually blue) buttons if standard selectors didn't work
            if not post_submit_clicked:
                logger.warning("Could not find 'Post' button with standard selectors, trying fallback method")
                
                try:
                    # Find all primary buttons (usually blue)
                    primary_buttons = await self.page.query_selector_all("button.artdeco-button--primary")
                    
                    # Click the first visible primary button
                    for button in primary_buttons:
                        is_visible = await button.is_visible()
                        if is_visible:
                            await button.click()
                            post_submit_clicked = True
                            logger.info("Clicked primary action button directly")
                            break
                except Exception as e:
                    logger.debug(f"Error with primary button approach: {str(e)}")
                
                # If still not clicked, use JavaScript as last resort
                if not post_submit_clicked:
                    try:
                        post_submit_clicked = await self.page.evaluate("""
                        () => {
                            // Try different approaches to find the post button
                            
                            // 1. Find post button by text content
                            const buttons = Array.from(document.querySelectorAll('button'));
                            const postButtonByText = buttons.find(btn => 
                                btn.textContent.trim() === 'Post' ||
                                btn.textContent.trim() === 'Share' ||
                                btn.textContent.trim() === 'Share post' ||
                                btn.textContent.trim() === 'Publish'
                            );
                            
                            if (postButtonByText) {
                                try {
                                    postButtonByText.click();
                                    console.log('Clicked post button by text:', postButtonByText.textContent);
                                    return true;
                                } catch (err) {
                                    console.error('Error clicking text post button:', err);
                                }
                            }
                            
                            // 2. Find primary action button (usually blue)
                            const primaryButtons = Array.from(document.querySelectorAll('button.artdeco-button--primary, button[type="submit"]'));
                            const primaryButton = primaryButtons.find(btn => btn.offsetParent !== null); // Check if button is visible
                            
                            if (primaryButton) {
                                try {
                                    primaryButton.click();
                                    console.log('Clicked primary action button');
                                    return true;
                                } catch (err) {
                                    console.error('Error clicking primary button:', err);
                                }
                            }
                            
                            // 3. Find any button inside share-actions div
                            const shareButtons = Array.from(document.querySelectorAll('.share-actions button, .share-box-footer button'));
                            const shareButton = shareButtons.find(btn => btn.offsetParent !== null);
                            
                            if (shareButton) {
                                try {
                                    shareButton.click();
                                    console.log('Clicked share actions button');
                                    return true;
                                } catch (err) {
                                    console.error('Error clicking share button:', err);
                                }
                            }
                            
                            // 4. Last resort: Try to find any button at the bottom of composer
                            const composerButtons = Array.from(document.querySelectorAll('.share-box_actions button, .share-box-footer button, .editor-footer button'));
                            if (composerButtons.length > 0) {
                                // Find button furthest to the right (usually the submit button)
                                composerButtons.sort((a, b) => {
                                    const rectA = a.getBoundingClientRect();
                                    const rectB = b.getBoundingClientRect();
                                    return rectB.right - rectA.right; // Sort by rightmost position
                                });
                                
                                const rightmostButton = composerButtons[0];
                                if (rightmostButton) {
                                    rightmostButton.click();
                                    console.log('Clicked rightmost button in composer footer');
                                    return true;
                                }
                            }
                            
                            return false;
                        }
                        """)
                    except Exception as e:
                        logger.error(f"Error with JavaScript post button finder: {str(e)}")
            
            if not post_submit_clicked:
                logger.error("Could not find 'Post' button")
                return {
                    "success": False,
                    "message": "Could not find the 'Post' button to submit your post."
                }
            
            # Wait for post to be submitted
            logger.info("Waiting for post to be submitted")
            
            try:
                # Track multiple potential success indicators
                toast_promise = self.page.wait_for_selector("div.artdeco-toast-item--visible", timeout=10000)
                feed_promise = self.page.wait_for_selector(".feed-shared-update-v2", timeout=10000)
                success_message_promise = self.page.wait_for_selector("div[aria-live='assertive']", timeout=10000)
                
                # Create a timeout promise
                async def wait_timeout():
                    await asyncio.sleep(8)
                    return True
                
                timeout_promise = asyncio.create_task(wait_timeout())
                
                # Wait for the first promise to resolve
                done, pending = await asyncio.wait(
                    [
                        asyncio.create_task(toast_promise), 
                        asyncio.create_task(feed_promise),
                        asyncio.create_task(success_message_promise),
                        timeout_promise
                    ],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel any pending tasks
                for task in pending:
                    task.cancel()
                
                # Assume success if any promise completed
                success_indicator = True
                
                if success_indicator:
                    logger.info("Successfully posted to LinkedIn")
                    return {
                        "success": True,
                        "message": "Successfully posted to LinkedIn"
                    }
                else:
                    logger.warning("Could not confirm if post was successful")
                    return {
                        "success": False,
                        "message": "Could not confirm if post was successful. Please check your LinkedIn feed."
                    }
            except Exception as e:
                logger.error(f"Error confirming post success: {str(e)}")
                return {
                    "success": False,
                    "message": f"Error confirming post success: {str(e)}"
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