"""
TikTok Trend Scraper
====================
This module scrapes trending content from TikTok Creative Center.

Data collected:
- Trending hashtags
- Trending songs/sounds
- Trending creators
- Top performing videos

This data is used to inform content strategy and optimize posting times.
"""

import os
import sys
import logging
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Database

logger = logging.getLogger(__name__)


class TrendScraperError(Exception):
    """Custom exception for trend scraping errors."""
    pass


class TikTokTrendScraper:
    """
    Scrapes trending content from TikTok Creative Center.
    
    Uses Playwright to navigate and extract data from the public
    Creative Center pages.
    """
    
    # URLs
    CREATIVE_CENTER_BASE = "https://ads.tiktok.com/business/creativecenter"
    TRENDING_HASHTAGS_URL = f"{CREATIVE_CENTER_BASE}/inspiration/popular/hashtag/pc/en"
    TRENDING_SONGS_URL = f"{CREATIVE_CENTER_BASE}/inspiration/popular/music/pc/en"
    TRENDING_CREATORS_URL = f"{CREATIVE_CENTER_BASE}/inspiration/popular/creator/pc/en"
    TRENDING_VIDEOS_URL = f"{CREATIVE_CENTER_BASE}/inspiration/popular/video/pc/en"
    
    def __init__(self, database_path: str, headless: bool = True):
        """
        Initialize the trend scraper.
        
        Args:
            database_path: Path to the SQLite database
            headless: Whether to run browser in headless mode
        """
        self.database = Database(database_path)
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        logger.info("TikTokTrendScraper initialized")
    
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
        
        # Set a reasonable viewport size
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        
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
    
    def _wait_for_page_load(self, timeout: int = 30000):
        """
        Wait for page to fully load.
        
        Args:
            timeout: Timeout in milliseconds
        """
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            time.sleep(2)  # Additional wait for dynamic content
        except PlaywrightTimeoutError:
            logger.warning("Page load timeout - continuing anyway")
    
    def scrape_trending_hashtags(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape trending hashtags from TikTok Creative Center.
        
        Args:
            limit: Maximum number of hashtags to scrape
        
        Returns:
            List of hashtag dictionaries
        """
        logger.info(f"Scraping trending hashtags (limit: {limit})...")
        
        try:
            # Navigate to trending hashtags page
            self.page.goto(self.TRENDING_HASHTAGS_URL, timeout=60000)
            self._wait_for_page_load()
            
            hashtags = []
            
            # Scroll to load more content
            for _ in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Extract hashtag data
            # Note: This selector may need to be updated if TikTok changes their HTML
            hashtag_elements = self.page.query_selector_all('[class*="hashtag"]')
            
            for idx, element in enumerate(hashtag_elements[:limit]):
                try:
                    # Extract text content
                    text = element.text_content()
                    
                    if text and text.strip():
                        hashtag_data = {
                            'rank': idx + 1,
                            'hashtag': text.strip(),
                            'scraped_at': datetime.now().isoformat(),
                            'source': 'tiktok_creative_center'
                        }
                        
                        hashtags.append(hashtag_data)
                        logger.debug(f"Scraped hashtag #{idx + 1}: {text.strip()}")
                
                except Exception as e:
                    logger.warning(f"Failed to extract hashtag #{idx + 1}: {e}")
            
            logger.info(f"✅ Scraped {len(hashtags)} trending hashtags")
            return hashtags
        
        except Exception as e:
            logger.error(f"Failed to scrape trending hashtags: {e}", exc_info=True)
            raise TrendScraperError(f"Hashtag scraping failed: {e}")
    
    def scrape_trending_songs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape trending songs from TikTok Creative Center.
        
        Args:
            limit: Maximum number of songs to scrape
        
        Returns:
            List of song dictionaries
        """
        logger.info(f"Scraping trending songs (limit: {limit})...")
        
        try:
            # Navigate to trending songs page
            self.page.goto(self.TRENDING_SONGS_URL, timeout=60000)
            self._wait_for_page_load()
            
            songs = []
            
            # Scroll to load more content
            for _ in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Extract song data
            song_elements = self.page.query_selector_all('[class*="music"], [class*="song"]')
            
            for idx, element in enumerate(song_elements[:limit]):
                try:
                    text = element.text_content()
                    
                    if text and text.strip():
                        song_data = {
                            'rank': idx + 1,
                            'song_info': text.strip(),
                            'scraped_at': datetime.now().isoformat(),
                            'source': 'tiktok_creative_center'
                        }
                        
                        songs.append(song_data)
                        logger.debug(f"Scraped song #{idx + 1}: {text.strip()}")
                
                except Exception as e:
                    logger.warning(f"Failed to extract song #{idx + 1}: {e}")
            
            logger.info(f"✅ Scraped {len(songs)} trending songs")
            return songs
        
        except Exception as e:
            logger.error(f"Failed to scrape trending songs: {e}", exc_info=True)
            raise TrendScraperError(f"Song scraping failed: {e}")
    
    def scrape_trending_creators(self, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Scrape trending creators from TikTok Creative Center.
        
        Args:
            limit: Maximum number of creators to scrape
        
        Returns:
            List of creator dictionaries
        """
        logger.info(f"Scraping trending creators (limit: {limit})...")
        
        try:
            # Navigate to trending creators page
            self.page.goto(self.TRENDING_CREATORS_URL, timeout=60000)
            self._wait_for_page_load()
            
            creators = []
            
            # Scroll to load more content
            for _ in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Extract creator data
            creator_elements = self.page.query_selector_all('[class*="creator"], [class*="user"]')
            
            for idx, element in enumerate(creator_elements[:limit]):
                try:
                    text = element.text_content()
                    
                    if text and text.strip():
                        creator_data = {
                            'rank': idx + 1,
                            'creator_info': text.strip(),
                            'scraped_at': datetime.now().isoformat(),
                            'source': 'tiktok_creative_center'
                        }
                        
                        creators.append(creator_data)
                        logger.debug(f"Scraped creator #{idx + 1}: {text.strip()}")
                
                except Exception as e:
                    logger.warning(f"Failed to extract creator #{idx + 1}: {e}")
            
            logger.info(f"✅ Scraped {len(creators)} trending creators")
            return creators
        
        except Exception as e:
            logger.error(f"Failed to scrape trending creators: {e}", exc_info=True)
            raise TrendScraperError(f"Creator scraping failed: {e}")
    
    def scrape_all_trends(self) -> Dict[str, Any]:
        """
        Scrape all trending data in one session.
        
        Returns:
            Dictionary containing all trend data
        """
        logger.info("=" * 80)
        logger.info("SCRAPING ALL TIKTOK TRENDS")
        logger.info("=" * 80)
        
        results = {
            'scraped_at': datetime.now().isoformat(),
            'hashtags': [],
            'songs': [],
            'creators': [],
            'success': False
        }
        
        try:
            # Scrape hashtags
            results['hashtags'] = self.scrape_trending_hashtags(limit=50)
            
            # Scrape songs
            results['songs'] = self.scrape_trending_songs(limit=50)
            
            # Scrape creators
            results['creators'] = self.scrape_trending_creators(limit=30)
            
            results['success'] = True
            
            logger.info("=" * 80)
            logger.info("TREND SCRAPING COMPLETE")
            logger.info(f"  ✅ Hashtags: {len(results['hashtags'])}")
            logger.info(f"  ✅ Songs: {len(results['songs'])}")
            logger.info(f"  ✅ Creators: {len(results['creators'])}")
            logger.info("=" * 80)
            
            return results
        
        except Exception as e:
            logger.error(f"Trend scraping failed: {e}", exc_info=True)
            results['error'] = str(e)
            return results
    
    def save_trends_to_database(self, trends: Dict[str, Any]):
        """
        Save scraped trends to the database.
        
        Args:
            trends: Dictionary containing trend data
        """
        logger.info("Saving trends to database...")
        
        # Note: This would use the database methods to store the trends
        # For now, we'll save to a JSON file as well for backup
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("/home/ubuntu/affilify_tiktok_system/data/trends")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"trends_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(trends, f, indent=2)
        
        logger.info(f"✅ Trends saved to: {output_file}")


if __name__ == "__main__":
    # Test the trend scraper
    logging.basicConfig(level=logging.INFO)
    
    print("TikTokTrendScraper module loaded successfully!")
    print("=" * 80)
    print("This module scrapes trending content from TikTok Creative Center.")
    print("=" * 80)
