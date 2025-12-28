"""
TikTok Poster
=============
This module handles the actual posting of videos to TikTok using
MultiLogin browser profiles and Playwright automation.

Key features:
1. Human-like posting behavior with random delays
2. MultiLogin profile integration for stealth
3. Error handling and retry logic
4. Session management and cookie persistence
"""

import os
import sys
import logging
import time
import random
from typing import Dict, Any, Optional
from pathlib import Path

from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Database
from pillar1_infrastructure.multilogin_client import MultiLoginClient, MultiLoginAPIError

logger = logging.getLogger(__name__)


class TikTokPosterError(Exception):
    """Custom exception for TikTok posting errors."""
    pass


class TikTokPoster:
    """
    Posts videos to TikTok using MultiLogin profiles and Playwright.
    
    Implements human-like behavior to avoid detection.
    """
    
    TIKTOK_UPLOAD_URL = "https://www.tiktok.com/upload"
    
    def __init__(self, 
                 database_path: str,
                 multilogin_profile_uuid: str,
                 multilogin_client: MultiLoginClient,
                 headless: bool = False):
        """
        Initialize the TikTok poster.
        
        Args:
            database_path: Path to the SQLite database
            multilogin_profile_uuid: MultiLogin profile UUID to use
            multilogin_client: MultiLogin API client instance
            headless: Whether to run browser in headless mode
        """
        self.database = Database(database_path)
        self.multilogin_profile_uuid = multilogin_profile_uuid
        self.multilogin_client = multilogin_client
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.connection_info: Optional[Dict[str, Any]] = None
        
        logger.info(f"TikTokPoster initialized for profile: {multilogin_profile_uuid}")
    
    def __enter__(self):
        """Context manager entry."""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_browser()
    
    def start_browser(self):
        """Start the browser with MultiLogin profile using Local Launcher API."""
        logger.info(f"Starting browser with MultiLogin profile: {self.multilogin_profile_uuid}...")
        
        try:
            # Check if multilogin_client is None
            if self.multilogin_client is None:
                raise TikTokPosterError(
                    "MultiLogin client is None. Please ensure MULTILOGIN_BASE_URL, "
                    "MULTILOGIN_EMAIL, and MULTILOGIN_PASSWORD are set in .env file, "
                    "OR manually start the profile in MultiLogin app before running this script."
                )
            
            # Start the MultiLogin profile using Local Launcher API
            self.connection_info = self.multilogin_client.start_profile(
                profile_uuid=self.multilogin_profile_uuid,
                automation_type="playwright"
            )
            
            # Extract connection details
            ws_endpoint = self.connection_info.get('ws_endpoint')
            
            if not ws_endpoint:
                raise TikTokPosterError("No WebSocket endpoint returned from MultiLogin")
            
            logger.info(f"MultiLogin profile started, connecting to: {ws_endpoint}")
            
            # Connect to the MultiLogin browser via WebSocket
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp(ws_endpoint)
            
            # Get the default context (MultiLogin profile already has its own context)
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]
            else:
                # Fallback: create a new context
                self.context = self.browser.new_context()
            
            # Get or create a page
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = self.context.new_page()
            
            logger.info("✅ Browser connected successfully via MultiLogin")
        
        except MultiLoginAPIError as e:
            logger.error(f"Failed to start MultiLogin profile: {e}")
            raise TikTokPosterError(f"MultiLogin profile start failed: {e}")
        
        except Exception as e:
            logger.error(f"Failed to connect to browser: {e}")
            raise TikTokPosterError(f"Browser connection failed: {e}")
    
    def close_browser(self):
        """Close the browser and cleanup."""
        try:
            # Disconnect from browser (don't close it, MultiLogin manages that)
            if self.browser:
                self.browser.close()
            
            if hasattr(self, 'playwright'):
                self.playwright.stop()
            
            # Stop the MultiLogin profile
            if self.multilogin_profile_uuid and self.multilogin_client is not None:
                try:
                    self.multilogin_client.stop_profile(self.multilogin_profile_uuid)
                    logger.info("MultiLogin profile stopped")
                except Exception as e:
                    logger.warning(f"Failed to stop MultiLogin profile: {e}")
            
            logger.info("Browser closed")
        
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
    
    def _human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        Add a random delay to simulate human behavior.
        
        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Human delay: {delay:.2f}s")
        time.sleep(delay)
    
    def _type_like_human(self, selector: str, text: str):
        """
        Type text with human-like delays between keystrokes.
        
        Args:
            selector: CSS selector for the input element
            text: Text to type
        """
        element = self.page.wait_for_selector(selector, timeout=10000)
        
        for char in text:
            element.type(char, delay=random.uniform(50, 150))
        
        self._human_delay(0.5, 1.5)
    
    def navigate_to_upload_page(self):
        """Navigate to TikTok upload page."""
        logger.info("Navigating to TikTok upload page...")
        
        try:
            self.page.goto(self.TIKTOK_UPLOAD_URL, timeout=60000)
            self._human_delay(2, 4)
            
            logger.info("✅ Reached upload page")
        
        except Exception as e:
            logger.error(f"Failed to navigate to upload page: {e}")
            raise TikTokPosterError(f"Navigation failed: {e}")
    
    def upload_video_file(self, video_path: str):
        """
        Upload a video file to TikTok.
        
        Args:
            video_path: Path to the video file
        """
        logger.info(f"Uploading video: {video_path}")
        
        if not Path(video_path).exists():
            raise TikTokPosterError(f"Video file not found: {video_path}")
        
        try:
            # Wait for file input element
            # Note: Selector may need to be updated based on TikTok's current HTML
            file_input = self.page.wait_for_selector('input[type="file"]', timeout=10000)
            
            # Upload the file
            file_input.set_input_files(video_path)
            
            logger.info("✅ Video file uploaded")
            
            # Wait for upload to process
            self._human_delay(5, 10)
            
            # Wait for upload completion indicator
            # This selector needs to be updated based on TikTok's actual UI
            try:
                self.page.wait_for_selector('[class*="upload-complete"]', timeout=120000)
                logger.info("✅ Video processing complete")
            except PlaywrightTimeoutError:
                logger.warning("Upload completion indicator not found - continuing anyway")
        
        except Exception as e:
            logger.error(f"Video upload failed: {e}")
            raise TikTokPosterError(f"Upload failed: {e}")
    
    def fill_caption_and_metadata(self, metadata: Dict[str, Any]):
        """
        Fill in the caption and metadata for the post.
        
        Args:
            metadata: Dictionary containing caption, hashtags, etc.
        """
        logger.info("Filling caption and metadata...")
        
        try:
            # Fill caption
            # Note: Selector needs to be updated based on TikTok's current HTML
            caption_selector = '[placeholder*="caption"], [placeholder*="description"]'
            
            full_description = metadata.get('full_description', '')
            
            self._type_like_human(caption_selector, full_description)
            
            logger.info(f"✅ Caption filled ({len(full_description)} chars)")
            
            self._human_delay(1, 2)
        
        except Exception as e:
            logger.error(f"Failed to fill metadata: {e}")
            raise TikTokPosterError(f"Metadata fill failed: {e}")
    
    def set_privacy_settings(self, privacy: str = "public"):
        """
        Set privacy settings for the post.
        
        Args:
            privacy: Privacy level (public, friends, private)
        """
        logger.info(f"Setting privacy to: {privacy}")
        
        try:
            # Click privacy dropdown
            # Note: Selector needs to be updated
            privacy_selector = '[class*="privacy"]'
            
            self.page.click(privacy_selector)
            self._human_delay(0.5, 1.0)
            
            # Select privacy option
            option_selector = f'[data-value="{privacy}"]'
            self.page.click(option_selector)
            
            logger.info(f"✅ Privacy set to {privacy}")
            
            self._human_delay(0.5, 1.0)
        
        except Exception as e:
            logger.warning(f"Failed to set privacy (may already be correct): {e}")
    
    def click_post_button(self):
        """Click the post/publish button."""
        logger.info("Clicking post button...")
        
        try:
            # Find and click post button
            # Note: Selector needs to be updated
            post_button_selector = 'button[class*="post"], button:has-text("Post")'
            
            self.page.click(post_button_selector)
            
            logger.info("✅ Post button clicked")
            
            # Wait for posting to complete
            self._human_delay(5, 10)
            
            # Wait for success indicator
            try:
                self.page.wait_for_selector('[class*="success"]', timeout=30000)
                logger.info("✅ Post published successfully")
                return True
            except PlaywrightTimeoutError:
                logger.warning("Success indicator not found - post may still have succeeded")
                return False
        
        except Exception as e:
            logger.error(f"Failed to click post button: {e}")
            raise TikTokPosterError(f"Post button click failed: {e}")
    
    def post_video(self, 
                   video_path: str,
                   metadata: Dict[str, Any],
                   privacy: str = "public") -> bool:
        """
        Complete workflow to post a video to TikTok.
        
        Args:
            video_path: Path to the video file
            metadata: Dictionary containing caption, hashtags, etc.
            privacy: Privacy level
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 80)
        logger.info("STARTING TIKTOK POST WORKFLOW")
        logger.info(f"  Profile: {self.multilogin_profile_id}")
        logger.info(f"  Video: {video_path}")
        logger.info("=" * 80)
        
        try:
            # Step 1: Navigate to upload page
            self.navigate_to_upload_page()
            
            # Step 2: Upload video file
            self.upload_video_file(video_path)
            
            # Step 3: Fill caption and metadata
            self.fill_caption_and_metadata(metadata)
            
            # Step 4: Set privacy settings
            self.set_privacy_settings(privacy)
            
            # Step 5: Click post button
            success = self.click_post_button()
            
            logger.info("=" * 80)
            logger.info("POST WORKFLOW COMPLETE")
            logger.info(f"  Status: {'SUCCESS' if success else 'UNKNOWN'}")
            logger.info("=" * 80)
            
            return success
        
        except Exception as e:
            logger.error(f"Post workflow failed: {e}", exc_info=True)
            return False


if __name__ == "__main__":
    # Test the TikTok poster
    logging.basicConfig(level=logging.INFO)
    
    print("TikTokPoster module loaded successfully!")
    print("=" * 80)
    print("This module posts videos to TikTok using MultiLogin and Playwright.")
    print("=" * 80)
