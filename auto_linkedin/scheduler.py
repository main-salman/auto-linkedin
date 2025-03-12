"""
Post scheduler for Auto LinkedIn
"""

import os
import threading
import time
import logging
import random
import json
import queue
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger(__name__)

class PostScheduler:
    """Scheduler for LinkedIn posts"""
    
    def __init__(self, linkedin_controller, config):
        """Initialize the post scheduler
        
        Args:
            linkedin_controller: LinkedIn browser controller
            config: Application configuration
        """
        self.linkedin_controller = linkedin_controller
        self.config = config
        self.posts_queue = queue.Queue()
        self.schedule_thread = None
        self.stop_event = threading.Event()
        self.is_running = False
        self.last_post_time = None
        
        # Status callback for UI updates
        self.status_callback = None
    
    def set_status_callback(self, callback):
        """Set a callback function for status updates
        
        Args:
            callback: Function that takes a status dict
        """
        self.status_callback = callback
    
    def add_post(self, post_data):
        """Add a post to the queue
        
        Args:
            post_data: Dictionary containing post information (text, media_files)
        
        Returns:
            bool: True if post was added, False otherwise
        """
        try:
            # Add timestamp for tracking
            post_data['queued_at'] = datetime.now().isoformat()
            post_data['status'] = 'queued'
            
            # Add to queue
            self.posts_queue.put(post_data)
            
            # Start scheduler if it's not running
            if not self.is_running:
                self.start()
            
            logger.info(f"Added post to queue. Queue size: {self.posts_queue.qsize()}")
            return True
        except Exception as e:
            logger.exception("Error adding post to queue")
            return False
    
    def start(self):
        """Start the post scheduler"""
        if self.is_running:
            logger.info("Scheduler is already running")
            return False
        
        logger.info("Starting post scheduler")
        
        # Reset stop event
        self.stop_event.clear()
        
        # Start the scheduler thread
        self.schedule_thread = threading.Thread(
            target=self._scheduler_loop,
            name="PostSchedulerThread",
            daemon=True
        )
        
        self.schedule_thread.start()
        self.is_running = True
        
        self._update_status()
        
        return True
    
    def stop(self):
        """Stop the post scheduler"""
        if not self.is_running:
            logger.info("Scheduler is not running")
            return False
        
        logger.info("Stopping post scheduler")
        
        # Signal the scheduler to stop
        self.stop_event.set()
        
        # Wait for the thread to stop (with timeout)
        if self.schedule_thread and self.schedule_thread.is_alive():
            self.schedule_thread.join(timeout=3.0)
        
        self.is_running = False
        self._update_status()
        
        return True
    
    def clear_queue(self):
        """Clear the post queue"""
        try:
            # Create a new queue
            self.posts_queue = queue.Queue()
            logger.info("Post queue cleared")
            
            self._update_status()
            return True
        except Exception as e:
            logger.exception("Error clearing post queue")
            return False
    
    def get_queue_size(self):
        """Get the current queue size
        
        Returns:
            int: Number of posts in queue
        """
        try:
            return self.posts_queue.qsize()
        except Exception:
            return 0
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        try:
            # Initial delay to allow UI to initialize
            time.sleep(2)
            
            while not self.stop_event.is_set():
                try:
                    # Get post interval from config (default to 30 minutes if not set)
                    post_interval_minutes = self.config.get('posting_interval_minutes', 30)
                    
                    # Add some randomness to the interval (+/- 10%)
                    variation_factor = random.uniform(0.9, 1.1)
                    actual_interval_minutes = max(5, post_interval_minutes * variation_factor)
                    
                    # Check if it's time to post
                    current_time = datetime.now()
                    
                    if self.last_post_time is None or (
                        current_time - self.last_post_time > timedelta(minutes=actual_interval_minutes)
                    ):
                        # Try to get a post from the queue (non-blocking)
                        try:
                            post_data = self.posts_queue.get_nowait()
                            
                            # Process the post
                            self._process_post(post_data)
                            
                            # Update last post time
                            self.last_post_time = current_time
                            
                            # Mark task as done
                            self.posts_queue.task_done()
                            
                        except queue.Empty:
                            # No posts in queue, continue looping
                            pass
                    
                    # Update status for UI
                    self._update_status()
                    
                    # Sleep for a short time before checking again
                    # (Use stop_event.wait() instead of time.sleep() to respect stop_event)
                    self.stop_event.wait(10)  # Check every 10 seconds
                
                except Exception as e:
                    logger.exception(f"Error in scheduler loop: {str(e)}")
                    # Sleep a bit longer after an error
                    self.stop_event.wait(30)
            
            logger.info("Scheduler loop stopped")
        
        except Exception as e:
            logger.exception(f"Scheduler thread crashed: {str(e)}")
            self.is_running = False
            self._update_status()
    
    def _process_post(self, post_data):
        """Process a post from the queue
        
        Args:
            post_data: Dictionary containing post information
        """
        logger.info(f"Processing post: {post_data.get('text', '')[:50]}...")
        
        try:
            # Extract post data
            text = post_data.get('text', '')
            media_files = post_data.get('media_files', [])
            
            if not text:
                logger.warning("Empty post text, skipping")
                post_data['status'] = 'error'
                post_data['error'] = 'Empty post text'
                return
            
            # Update status
            post_data['status'] = 'processing'
            post_data['processing_started_at'] = datetime.now().isoformat()
            self._update_status()
            
            # Check if LinkedIn controller is initialized
            if not self.linkedin_controller.is_initialized:
                logger.info("LinkedIn controller not initialized, initializing...")
                
                # Initialize browser
                self.linkedin_controller.check_login_status()
            
            # Post to LinkedIn
            result = self.linkedin_controller.post_to_linkedin(text, media_files)
            
            # Update post data with result
            post_data['status'] = 'completed' if result.get('success', False) else 'error'
            post_data['completed_at'] = datetime.now().isoformat()
            post_data['result'] = result
            
            if result.get('success', False):
                logger.info("Post successfully published to LinkedIn")
                
                # Add to history
                self._add_to_history(post_data)
            else:
                logger.error(f"Failed to post to LinkedIn: {result.get('message', 'Unknown error')}")
                
                # Add error information
                post_data['error'] = result.get('message', 'Unknown error')
                
                # Add to errors in config
                error_info = {
                    'timestamp': datetime.now().isoformat(),
                    'error': result.get('message', 'Unknown error'),
                    'post_text': text[:100] + ('...' if len(text) > 100 else '')
                }
                self.config.add_error(error_info)
        
        except Exception as e:
            logger.exception(f"Error processing post: {str(e)}")
            
            # Update post data with error
            post_data['status'] = 'error'
            post_data['error'] = str(e)
            post_data['completed_at'] = datetime.now().isoformat()
        
        finally:
            # Update status for UI
            self._update_status()
    
    def _add_to_history(self, post_data):
        """Add post to history in config
        
        Args:
            post_data: Post data dictionary
        """
        try:
            # Create history entry
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'text': post_data.get('text', '')[:150] + ('...' if len(post_data.get('text', '')) > 150 else ''),
                'media_count': len(post_data.get('media_files', [])),
                'status': 'published'
            }
            
            # Add to config history
            self.config.add_to_history(history_entry)
        except Exception as e:
            logger.exception(f"Error adding post to history: {str(e)}")
    
    def _update_status(self):
        """Update status information and notify UI if callback is set"""
        if self.status_callback:
            try:
                status = {
                    'is_running': self.is_running,
                    'queue_size': self.get_queue_size(),
                    'last_post_time': self.last_post_time.isoformat() if self.last_post_time else None,
                    'next_post_time': self._get_next_post_time().isoformat() if self.last_post_time else None
                }
                
                self.status_callback(status)
            except Exception as e:
                logger.exception(f"Error updating status: {str(e)}")
    
    def _get_next_post_time(self):
        """Calculate the next scheduled post time
        
        Returns:
            datetime: Next post time
        """
        if not self.last_post_time:
            return datetime.now()
        
        post_interval_minutes = self.config.get('posting_interval_minutes', 30)
        
        # Add some randomness to the interval (+/- 10%)
        variation_factor = random.uniform(0.9, 1.1)
        actual_interval_minutes = max(5, post_interval_minutes * variation_factor)
        
        return self.last_post_time + timedelta(minutes=actual_interval_minutes) 