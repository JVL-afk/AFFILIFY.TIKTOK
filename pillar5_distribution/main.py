"""
Pillar 5 Main Script
====================
Main entry point for the Distribution and Stealth Posting System.

Usage:
    python main.py --dry-run
    python main.py --execute
    python main.py --schedule-only
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pillar5_distribution.posting_scheduler import PostingScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load configuration from environment variables."""
    env_path = Path(__file__).parent.parent / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
    
    config = {
        'database_path': os.getenv(
            'DATABASE_PATH',
            '/home/ubuntu/affilify_tiktok_system/data/affilify_system.db'
        )
    }
    
    return config


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Affilify Distribution System (Pillar 5)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no actual posting)'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the posting schedule'
    )
    
    parser.add_argument(
        '--schedule-only',
        action='store_true',
        help='Create schedule without executing'
    )
    
    parser.add_argument(
        '--start-time',
        type=str,
        help='Start time for posting window (ISO format)'
    )
    
    parser.add_argument(
        '--end-time',
        type=str,
        help='End time for posting window (ISO format)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Initialize scheduler
    scheduler = PostingScheduler(database_path=config['database_path'])
    
    # Parse times
    start_time = None
    end_time = None
    
    if args.start_time:
        start_time = datetime.fromisoformat(args.start_time)
    
    if args.end_time:
        end_time = datetime.fromisoformat(args.end_time)
    
    # Load resources
    logger.info("Loading resources...")
    profiles = scheduler.load_profiles()
    videos = scheduler.load_processed_videos()
    
    # For demo purposes, assume we have 60 of each
    if not profiles:
        logger.warning("No profiles loaded - using placeholder data")
        profiles = [{'name': f'Profile_{i}', 'multilogin_id': f'profile_{i}'} for i in range(60)]
    
    if not videos:
        logger.warning("No videos loaded - using placeholder data")
        videos = [{'output_path': f'/path/to/video_{i}.mp4', 'feature': 'Create Website'} for i in range(60)]
    
    # Load metadata for the first video's feature
    feature = videos[0].get('feature', 'Create Website')
    metadata_list = scheduler.load_metadata(feature)
    
    if not metadata_list:
        logger.warning("No metadata loaded - using placeholder data")
        metadata_list = [{'full_description': f'Caption {i}', 'hashtags': []} for i in range(60)]
    
    # Create assignments
    assignments = scheduler.assign_posts_to_accounts(videos, metadata_list, profiles)
    
    # Create schedule
    scheduled_times = scheduler.create_posting_schedule(
        num_posts=len(assignments),
        start_time=start_time,
        end_time=end_time
    )
    
    if args.schedule_only:
        logger.info("Schedule created (not executing):")
        for idx, (assignment, time) in enumerate(zip(assignments, scheduled_times)):
            logger.info(f"  {idx + 1}. {time} - {assignment['profile']['name']}")
    
    elif args.execute or args.dry_run:
        scheduler.execute_posting_schedule(
            assignments=assignments,
            scheduled_times=scheduled_times,
            dry_run=args.dry_run
        )
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
