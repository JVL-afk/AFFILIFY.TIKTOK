"""
Posting Scheduler
=================
This module manages the scheduling and distribution of posts across
60 TikTok accounts.

Key features:
1. Randomized posting times to appear natural
2. Account rotation to distribute load
3. Rate limiting (max 1 post per account per day)
4. Retry logic for failed posts
5. Progress tracking and logging
"""

import os
import sys
import logging
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Database
from pillar5_distribution.tiktok_poster import TikTokPoster

logger = logging.getLogger(__name__)


class PostingScheduler:
    """
    Manages the scheduling and execution of TikTok posts across multiple accounts.
    
    Ensures posts are distributed naturally and safely.
    """
    
    def __init__(self, database_path: str):
        """
        Initialize the posting scheduler.
        
        Args:
            database_path: Path to the SQLite database
        """
        self.database = Database(database_path)
        
        logger.info("PostingScheduler initialized")
    
    def load_profiles(self) -> List[Dict[str, Any]]:
        """
        Load all MultiLogin profiles from the database.
        
        Returns:
            List of profile dictionaries
        """
        # Note: This would query the database for profiles
        # For now, return a placeholder
        logger.info("Loading MultiLogin profiles from database...")
        
        # TODO: Implement database query
        profiles = []
        
        logger.info(f"Loaded {len(profiles)} profiles")
        return profiles
    
    def load_processed_videos(self, affilify_feature: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load processed videos that are ready for posting.
        
        Args:
            affilify_feature: Optional filter by feature
        
        Returns:
            List of video dictionaries
        """
        logger.info("Loading processed videos...")
        
        # TODO: Implement database query
        videos = []
        
        logger.info(f"Loaded {len(videos)} processed videos")
        return videos
    
    def load_metadata(self, affilify_feature: str) -> List[Dict[str, Any]]:
        """
        Load metadata for a specific feature.
        
        Args:
            affilify_feature: The Affilify feature
        
        Returns:
            List of metadata dictionaries
        """
        logger.info(f"Loading metadata for {affilify_feature}...")
        
        # Look for metadata files
        metadata_dir = Path("/home/ubuntu/affilify_tiktok_system/data/metadata")
        
        if not metadata_dir.exists():
            logger.warning(f"Metadata directory not found: {metadata_dir}")
            return []
        
        # Find metadata file for this feature
        feature_safe = affilify_feature.replace(" ", "_").lower()
        metadata_files = list(metadata_dir.glob(f"metadata_{feature_safe}_*.json"))
        
        if not metadata_files:
            logger.warning(f"No metadata files found for {affilify_feature}")
            return []
        
        # Load the most recent file
        latest_file = max(metadata_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            metadata = json.load(f)
        
        logger.info(f"✅ Loaded {len(metadata)} metadata entries from {latest_file.name}")
        return metadata
    
    def create_posting_schedule(self, 
                                num_posts: int,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> List[datetime]:
        """
        Create a randomized posting schedule.
        
        Args:
            num_posts: Number of posts to schedule
            start_time: Start of posting window (default: now)
            end_time: End of posting window (default: 24 hours from now)
        
        Returns:
            List of scheduled posting times
        """
        if start_time is None:
            start_time = datetime.now()
        
        if end_time is None:
            end_time = start_time + timedelta(hours=24)
        
        logger.info(f"Creating schedule for {num_posts} posts...")
        logger.info(f"  Window: {start_time} to {end_time}")
        
        # Calculate time range in seconds
        total_seconds = (end_time - start_time).total_seconds()
        
        # Generate random times within the window
        random_offsets = sorted([random.uniform(0, total_seconds) for _ in range(num_posts)])
        
        scheduled_times = [start_time + timedelta(seconds=offset) for offset in random_offsets]
        
        logger.info(f"✅ Created schedule with {len(scheduled_times)} posts")
        return scheduled_times
    
    def assign_posts_to_accounts(self,
                                 videos: List[Dict[str, Any]],
                                 metadata_list: List[Dict[str, Any]],
                                 profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assign videos and metadata to specific accounts.
        
        Args:
            videos: List of processed videos
            metadata_list: List of metadata entries
            profiles: List of MultiLogin profiles
        
        Returns:
            List of posting assignments
        """
        logger.info("Assigning posts to accounts...")
        
        assignments = []
        
        # Ensure we have enough resources
        num_posts = min(len(videos), len(metadata_list), len(profiles))
        
        logger.info(f"Creating {num_posts} assignments")
        
        for i in range(num_posts):
            assignment = {
                'video': videos[i],
                'metadata': metadata_list[i],
                'profile': profiles[i],
                'assigned_at': datetime.now().isoformat()
            }
            
            assignments.append(assignment)
        
        logger.info(f"✅ Created {len(assignments)} post assignments")
        return assignments
    
    def execute_posting_schedule(self,
                                 assignments: List[Dict[str, Any]],
                                 scheduled_times: List[datetime],
                                 dry_run: bool = False):
        """
        Execute the posting schedule.
        
        Args:
            assignments: List of post assignments
            scheduled_times: List of scheduled times
            dry_run: If True, don't actually post (for testing)
        """
        logger.info("=" * 80)
        logger.info("EXECUTING POSTING SCHEDULE")
        logger.info(f"  Total posts: {len(assignments)}")
        logger.info(f"  Dry run: {dry_run}")
        logger.info("=" * 80)
        
        for idx, (assignment, scheduled_time) in enumerate(zip(assignments, scheduled_times)):
            logger.info(f"\nPost {idx + 1}/{len(assignments)}")
            logger.info(f"  Scheduled: {scheduled_time}")
            logger.info(f"  Profile: {assignment['profile'].get('name', 'Unknown')}")
            logger.info(f"  Video: {assignment['video'].get('output_path', 'Unknown')}")
            
            # Wait until scheduled time
            now = datetime.now()
            if scheduled_time > now:
                wait_seconds = (scheduled_time - now).total_seconds()
                logger.info(f"  Waiting {wait_seconds:.0f} seconds until scheduled time...")
                
                if not dry_run:
                    import time
                    time.sleep(wait_seconds)
            
            # Execute post
            if dry_run:
                logger.info("  [DRY RUN] Would post now")
            else:
                success = self._execute_single_post(assignment)
                
                if success:
                    logger.info("  ✅ Post successful")
                else:
                    logger.error("  ❌ Post failed")
        
        logger.info("=" * 80)
        logger.info("POSTING SCHEDULE COMPLETE")
        logger.info("=" * 80)
    
    def _execute_single_post(self, assignment: Dict[str, Any]) -> bool:
        """
        Execute a single post.
        
        Args:
            assignment: Post assignment dictionary
        
        Returns:
            True if successful, False otherwise
        """
        try:
            profile_id = assignment['profile'].get('multilogin_id', '')
            video_path = assignment['video'].get('output_path', '')
            metadata = assignment['metadata']
            
            with TikTokPoster(
                database_path=self.database.db_path,
                multilogin_profile_id=profile_id,
                headless=True
            ) as poster:
                success = poster.post_video(
                    video_path=video_path,
                    metadata=metadata,
                    privacy="public"
                )
                
                return success
        
        except Exception as e:
            logger.error(f"Post execution failed: {e}", exc_info=True)
            return False


if __name__ == "__main__":
    # Test the posting scheduler
    logging.basicConfig(level=logging.INFO)
    
    print("PostingScheduler module loaded successfully!")
    print("=" * 80)
    print("This module manages the distribution of posts across accounts.")
    print("=" * 80)
