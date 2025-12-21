"""
Pillar 2 Main Script
====================
Main entry point for the Content Ingestion and Processing System.

Usage:
    python main.py --video path/to/video.mp4 --feature "Create Website"
    python main.py --process-all
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pillar2_content_processing.batch_processor import BatchProcessor

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
        'raw_video_input_dir': os.getenv(
            'RAW_VIDEO_INPUT_DIR',
            '/home/ubuntu/affilify_tiktok_system/data/raw_videos'
        ),
        'processed_video_output_dir': os.getenv(
            'PROCESSED_VIDEO_OUTPUT_DIR',
            '/home/ubuntu/affilify_tiktok_system/data/processed_videos'
        ),
        'database_path': os.getenv(
            'DATABASE_PATH',
            '/home/ubuntu/affilify_tiktok_system/data/affilify_system.db'
        ),
        'temp_dir': os.getenv(
            'TEMP_DIR',
            '/tmp/affilify_processing'
        )
    }
    
    return config


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Affilify Content Processing System (Pillar 2)'
    )
    
    parser.add_argument(
        '--video',
        type=str,
        help='Path to a specific video to process'
    )
    
    parser.add_argument(
        '--feature',
        type=str,
        help='Affilify feature name (e.g., "Create Website")'
    )
    
    parser.add_argument(
        '--variations',
        type=int,
        default=60,
        help='Number of unique variations to create (default: 60)'
    )
    
    parser.add_argument(
        '--process-all',
        action='store_true',
        help='Process all pending videos in the raw input directory'
    )
    
    parser.add_argument(
        '--no-overlay',
        action='store_true',
        help='Skip text overlay'
    )
    
    parser.add_argument(
        '--split',
        action='store_true',
        help='Split video into clips'
    )
    
    parser.add_argument(
        '--clip-duration',
        type=int,
        default=30,
        help='Duration of each clip in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Initialize batch processor
    processor = BatchProcessor(config)
    
    if args.process_all:
        # Process all pending videos
        logger.info("Processing all pending videos...")
        processor.process_all_pending_videos(
            num_variations_per_video=args.variations
        )
    
    elif args.video and args.feature:
        # Process a specific video
        logger.info(f"Processing video: {args.video}")
        logger.info(f"Feature: {args.feature}")
        
        results = processor.process_raw_video(
            raw_video_path=args.video,
            affilify_feature=args.feature,
            num_variations=args.variations,
            add_text_overlay=not args.no_overlay,
            split_into_clips=args.split,
            clip_duration=args.clip_duration
        )
        
        if results['success']:
            logger.info("✅ Processing completed successfully!")
            logger.info(f"Created {len(results['processed_videos'])} unique variations")
        else:
            logger.error(f"❌ Processing failed: {results.get('error')}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
