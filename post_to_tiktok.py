#!/usr/bin/env python3
"""
Post to TikTok - Complete Posting Script
=========================================
Posts videos to TikTok using MultiLogin profiles.

Usage:
    python3 post_to_tiktok.py \\
        --video-dir data/final_clips \\
        --caption-dir data/batch_output/captions \\
        --accounts 5 \\
        --posts-per-account 2 \\
        --delay-minutes 5
"""

import os
import sys
import logging
import argparse
import time
import random
from pathlib import Path
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.database import Database
from pillar1_infrastructure.multilogin_client import MultiLoginClient
from pillar5_distribution.tiktok_poster import TikTokPoster

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_videos_and_captions(video_dir: Path, caption_dir: Path) -> List[Tuple[Path, Path]]:
    """
    Load video files and their corresponding caption files.
    
    Returns:
        List of (video_path, caption_path) tuples
    """
    video_files = sorted(video_dir.glob("*.mp4"))
    
    pairs = []
    for video_file in video_files:
        # Try multiple caption naming patterns
        # Pattern 1: video.mp4 -> video.txt
        caption_file = caption_dir / f"{video_file.stem}.txt"
        
        # Pattern 2: video.mp4 -> video.mp4.txt (what we actually have!)
        if not caption_file.exists():
            caption_file = caption_dir / f"{video_file.name}.txt"
        
        if caption_file.exists():
            pairs.append((video_file, caption_file))
        else:
            logger.warning(f"No caption found for {video_file.name}, skipping...")
    
    return pairs


def load_caption(caption_path: Path) -> str:
    """Load caption text from file."""
    with open(caption_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def post_videos(video_dir: str,
                caption_dir: str,
                accounts: int = 5,
                posts_per_account: int = 2,
                delay_minutes: int = 5,
                database_path: str = "data/affilify_tiktok.db"):
    """
    Post videos to TikTok accounts.
    
    Args:
        video_dir: Directory containing final video clips
        caption_dir: Directory containing caption files
        accounts: Number of accounts to use
        posts_per_account: Number of posts per account
        delay_minutes: Delay between posts (in minutes)
        database_path: Path to database
    """
    video_dir = Path(video_dir)
    caption_dir = Path(caption_dir)
    
    # Load videos and captions
    logger.info("Loading videos and captions...")
    video_caption_pairs = load_videos_and_captions(video_dir, caption_dir)
    
    if not video_caption_pairs:
        logger.error("No video-caption pairs found!")
        return
    
    logger.info(f"Found {len(video_caption_pairs)} video-caption pairs")
    
    # Load profiles from database
    logger.info("Loading MultiLogin profiles...")
    db = Database(database_path)
    all_profiles = db.get_all_profiles()
    
    if not all_profiles:
        logger.error("No profiles found in database!")
        logger.error("Run: python3 pillar1_infrastructure/manual_profile_loader.py --csv data/profile_mapping.csv")
        return
    
    logger.info(f"Found {len(all_profiles)} profiles in database")
    
    # Select profiles to use
    profiles_to_use = all_profiles[:accounts]
    logger.info(f"Using {len(profiles_to_use)} profiles")
    
    # Calculate total posts
    total_posts = min(len(video_caption_pairs), accounts * posts_per_account)
    logger.info(f"Will make {total_posts} posts ({accounts} accounts × {posts_per_account} posts)")
    
    # Initialize MultiLogin client with credentials from environment
    multilogin_base_url = os.getenv('MULTILOGIN_BASE_URL', 'http://localhost:35000')
    multilogin_email = os.getenv('MULTILOGIN_EMAIL', '')
    multilogin_password = os.getenv('MULTILOGIN_PASSWORD', '')
    
    if not multilogin_email or not multilogin_password:
        logger.warning("MultiLogin credentials not found in .env file")
        logger.warning("Using Local Launcher API without authentication")
        multilogin_client = None
    else:
        multilogin_client = MultiLoginClient(
            base_url=multilogin_base_url,
            email=multilogin_email,
            password=multilogin_password
        )
    
    # Post videos
    logger.info("\n" + "=" * 80)
    logger.info("STARTING TIKTOK POSTING")
    logger.info("=" * 80 + "\n")
    
    post_count = 0
    successful_posts = 0
    failed_posts = 0
    
    for account_idx, profile in enumerate(profiles_to_use, 1):
        profile_name = profile.get('name', 'Unknown')
        profile_uuid = profile.get('uuid', '')
        
        logger.info(f"\n{'=' * 80}")
        logger.info(f"ACCOUNT {account_idx}/{len(profiles_to_use)}: {profile_name}")
        logger.info(f"{'=' * 80}\n")
        
        # Post videos for this account
        for post_idx in range(posts_per_account):
            if post_count >= total_posts:
                break
            
            video_path, caption_path = video_caption_pairs[post_count]
            caption_text = load_caption(caption_path)
            
            logger.info(f"Post {post_count + 1}/{total_posts}")
            logger.info(f"  Account: {profile_name}")
            logger.info(f"  Video: {video_path.name}")
            logger.info(f"  Caption: {caption_text[:50]}...")
            
            try:
                # Create TikTok poster
                with TikTokPoster(
                    database_path=database_path,
                    multilogin_profile_uuid=profile_uuid,
                    multilogin_client=multilogin_client,
                    headless=False  # Show browser for debugging
                ) as poster:
                    # Post video
                    success = poster.post_video(
                        video_path=str(video_path),
                        caption=caption_text,
                        privacy="public"
                    )
                    
                    if success:
                        logger.info(f"  ✅ Post successful!")
                        successful_posts += 1
                    else:
                        logger.error(f"  ❌ Post failed!")
                        failed_posts += 1
            
            except Exception as e:
                logger.error(f"  ❌ Error posting: {e}")
                failed_posts += 1
            
            post_count += 1
            
            # Delay between posts (human-like behavior)
            if post_count < total_posts:
                delay_seconds = delay_minutes * 60
                # Add random variation (±20%)
                delay_seconds = int(delay_seconds * random.uniform(0.8, 1.2))
                
                logger.info(f"  Waiting {delay_seconds} seconds before next post...")
                time.sleep(delay_seconds)
        
        if post_count >= total_posts:
            break
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("POSTING COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total posts attempted: {post_count}")
    logger.info(f"Successful: {successful_posts}")
    logger.info(f"Failed: {failed_posts}")
    logger.info(f"Success rate: {(successful_posts/post_count*100) if post_count > 0 else 0:.1f}%")
    logger.info("=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Post videos to TikTok using MultiLogin profiles"
    )
    parser.add_argument(
        '--video-dir',
        required=True,
        help='Directory containing final video clips'
    )
    parser.add_argument(
        '--caption-dir',
        required=True,
        help='Directory containing caption files'
    )
    parser.add_argument(
        '--accounts',
        type=int,
        default=5,
        help='Number of accounts to use (default: 5)'
    )
    parser.add_argument(
        '--posts-per-account',
        type=int,
        default=2,
        help='Number of posts per account (default: 2)'
    )
    parser.add_argument(
        '--delay-minutes',
        type=int,
        default=5,
        help='Delay between posts in minutes (default: 5)'
    )
    parser.add_argument(
        '--database',
        default='data/affilify_system.db',
        help='Path to database (default: data/affilify_system.db)'
    )
    
    args = parser.parse_args()
    
    post_videos(
        video_dir=args.video_dir,
        caption_dir=args.caption_dir,
        accounts=args.accounts,
        posts_per_account=args.posts_per_account,
        delay_minutes=args.delay_minutes,
        database_path=args.database
    )


if __name__ == "__main__":
    main()
