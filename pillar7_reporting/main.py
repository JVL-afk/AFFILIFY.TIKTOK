"""
Pillar 7 Main Script
====================
Main entry point for the Reporting and Feedback System.

Usage:
    python main.py --daily-report
    python main.py --email-report
    python main.py --video-requests
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pillar7_reporting.report_generator import ReportGenerator

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
        ),
        'reports_dir': os.getenv(
            'REPORTS_DIR',
            '/home/ubuntu/affilify_tiktok_system/data/reports'
        )
    }
    
    return config


def generate_daily_report(config: dict):
    """Generate and save the daily report."""
    logger.info("Generating daily report...")
    
    generator = ReportGenerator(database_path=config['database_path'])
    
    # Generate full report
    report = generator.generate_full_report()
    
    # Save JSON report
    report_file = generator.save_report(report, config['reports_dir'])
    
    # Generate human-readable version
    text_report = generator.generate_human_readable_report(report)
    
    # Save text version
    text_file = report_file.with_suffix('.txt')
    with open(text_file, 'w') as f:
        f.write(text_report)
    
    logger.info(f"✅ Text report saved to: {text_file}")
    
    # Print to console
    print(text_report)


def generate_video_requests(config: dict):
    """Generate raw video requests only."""
    logger.info("Generating video requests...")
    
    generator = ReportGenerator(database_path=config['database_path'])
    
    requests = generator.generate_raw_video_requests()
    
    print("\n" + "=" * 80)
    print("RAW VIDEO REQUESTS")
    print("=" * 80 + "\n")
    
    for req in requests:
        print(f"Feature: {req['feature']} (Priority: {req['priority']})")
        print(f"  Reason: {req['reason']}")
        print(f"  Focus: {req['suggested_focus']}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Affilify Reporting System (Pillar 7)'
    )
    
    parser.add_argument(
        '--daily-report',
        action='store_true',
        help='Generate daily report'
    )
    
    parser.add_argument(
        '--video-requests',
        action='store_true',
        help='Generate raw video requests'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if args.daily_report:
        generate_daily_report(config)
    
    elif args.video_requests:
        generate_video_requests(config)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
