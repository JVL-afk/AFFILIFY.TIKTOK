"""
Performance Scraper
===================
This module scrapes performance metrics for posted videos.

Key metrics:
1. Views
2. Likes
3. Comments
4. Shares
5. Engagement rate
6. Watch time (if available)
"""

import os
import sys
import logging
import time
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from playwright.sync_api import sync_playwright, Page, Browser

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Database

logger = logging.getLogger(__name__)


class PerformanceScraper:
    """
    Scrapes performance metrics for TikTok videos.
    
    Uses Playwright to navigate to video pages and extract metrics.
    """
    
    def __init__(self, database_path: str, headless: bool = True):
        """
        Initialize the performance scraper.
        
        Args:
            database_path: Path to the SQLite database
            headless: Whether to run browser in headless mode
        """
        self.database = Database(database_path)
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        logger.info("PerformanceScraper initialized")
    
    def __enter__(self):
        """Context manager entry."""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_browser()
    
    def start_browser(self):
        """Start the Playwright browser."""
        logger.info("Starting browser...")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        
        logger.info("Browser started successfully")
    
    def close_browser(self):
        """Close the browser and cleanup."""
        if self.page:
            self.page.close()
        
        if self.browser:
            self.browser.close()
        
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        
        logger.info("Browser closed")
    
    def scrape_video_metrics(self, video_url: str) -> Dict[str, Any]:
        """
        Scrape performance metrics for a single video.
        
        Args:
            video_url: URL of the TikTok video
        
        Returns:
            Dictionary containing metrics
        """
        logger.info(f"Scraping metrics for: {video_url}")
        
        metrics = {
            'video_url': video_url,
            'scraped_at': datetime.now().isoformat(),
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'engagement_rate': 0.0,
            'success': False
        }
        
        try:
            # Navigate to video page
            self.page.goto(video_url, timeout=60000)
            time.sleep(3)  # Wait for dynamic content
            
            # Extract metrics
            # Note: Selectors need to be updated based on TikTok's current HTML
            
            # Views
            try:
                views_text = self.page.text_content('[class*="view"], [data-e2e="views"]')
                metrics['views'] = self._parse_metric_text(views_text)
            except Exception as e:
                logger.warning(f"Failed to extract views: {e}")
            
            # Likes
            try:
                likes_text = self.page.text_content('[class*="like"], [data-e2e="likes"]')
                metrics['likes'] = self._parse_metric_text(likes_text)
            except Exception as e:
                logger.warning(f"Failed to extract likes: {e}")
            
            # Comments
            try:
                comments_text = self.page.text_content('[class*="comment"], [data-e2e="comments"]')
                metrics['comments'] = self._parse_metric_text(comments_text)
            except Exception as e:
                logger.warning(f"Failed to extract comments: {e}")
            
            # Shares
            try:
                shares_text = self.page.text_content('[class*="share"], [data-e2e="shares"]')
                metrics['shares'] = self._parse_metric_text(shares_text)
            except Exception as e:
                logger.warning(f"Failed to extract shares: {e}")
            
            # Calculate engagement rate
            if metrics['views'] > 0:
                total_engagement = metrics['likes'] + metrics['comments'] + metrics['shares']
                metrics['engagement_rate'] = (total_engagement / metrics['views']) * 100
            
            metrics['success'] = True
            
            logger.info(f"✅ Metrics: {metrics['views']} views, {metrics['likes']} likes, "
                       f"{metrics['comments']} comments, {metrics['shares']} shares")
        
        except Exception as e:
            logger.error(f"Failed to scrape metrics: {e}", exc_info=True)
            metrics['error'] = str(e)
        
        return metrics
    
    def _parse_metric_text(self, text: str) -> int:
        """
        Parse metric text (e.g., "1.2K", "5.3M") to integer.
        
        Args:
            text: Metric text
        
        Returns:
            Integer value
        """
        if not text:
            return 0
        
        # Remove non-numeric characters except K, M, B, and decimal point
        text = text.strip().upper()
        
        # Extract number and suffix
        match = re.search(r'([\d.]+)([KMB])?', text)
        
        if not match:
            return 0
        
        number = float(match.group(1))
        suffix = match.group(2)
        
        # Convert based on suffix
        multipliers = {
            'K': 1_000,
            'M': 1_000_000,
            'B': 1_000_000_000
        }
        
        multiplier = multipliers.get(suffix, 1)
        
        return int(number * multiplier)
    
    def scrape_batch_metrics(self, video_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape metrics for multiple videos.
        
        Args:
            video_urls: List of video URLs
        
        Returns:
            List of metrics dictionaries
        """
        logger.info(f"Scraping metrics for {len(video_urls)} videos...")
        
        all_metrics = []
        
        for idx, url in enumerate(video_urls):
            logger.info(f"Progress: {idx + 1}/{len(video_urls)}")
            
            metrics = self.scrape_video_metrics(url)
            all_metrics.append(metrics)
            
            # Add delay between requests
            if idx < len(video_urls) - 1:
                time.sleep(2)
        
        logger.info(f"✅ Scraped metrics for {len(all_metrics)} videos")
        return all_metrics


if __name__ == "__main__":
    # Test the performance scraper
    logging.basicConfig(level=logging.INFO)
    
    print("PerformanceScraper module loaded successfully!")
    print("=" * 80)
    print("This module scrapes performance metrics for TikTok videos.")
    print("=" * 80)
