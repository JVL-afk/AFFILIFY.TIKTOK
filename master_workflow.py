"""
Master Workflow
===============
This is the master orchestration script that runs the complete
Affilify TikTok Content Distribution System.

It coordinates all 7 pillars to create a fully automated workflow.

Usage:
    python master_workflow.py --setup
    python master_workflow.py --daily-run
    python master_workflow.py --full-pipeline
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/affilify_tiktok_system/logs/master_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MasterWorkflow:
    """
    Master orchestration class that coordinates all 7 pillars.
    
    This is the Diamond Factory in action.
    """
    
    def __init__(self, config_path: str = '.env'):
        """
        Initialize the master workflow.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.load_configuration()
        
        logger.info("MasterWorkflow initialized")
    
    def load_configuration(self):
        """Load configuration from .env file."""
        if self.config_path.exists():
            load_dotenv(self.config_path)
            logger.info(f"Configuration loaded from {self.config_path}")
        else:
            logger.warning(f"Configuration file not found: {self.config_path}")
    
    def run_setup(self):
        """
        Run initial setup (Pillar 1).
        
        This creates all MultiLogin profiles with Nodemaven proxies.
        """
        logger.info("=" * 80)
        logger.info("RUNNING INITIAL SETUP (PILLAR 1)")
        logger.info("=" * 80)
        
        # Import Pillar 1
        from pillar1_infrastructure.profile_creator import ProfileCreator
        
        # Create profiles
        creator = ProfileCreator(
            database_path=os.getenv('DATABASE_PATH'),
            multilogin_api_url=os.getenv('MULTILOGIN_API_URL'),
            multilogin_api_token=os.getenv('MULTILOGIN_API_TOKEN')
        )
        
        creator.create_all_profiles()
        
        logger.info("✅ Setup complete")
    
    def run_trend_analysis(self):
        """
        Run trend analysis (Pillar 3).
        
        This scrapes current TikTok trends and analyzes them.
        """
        logger.info("=" * 80)
        logger.info("RUNNING TREND ANALYSIS (PILLAR 3)")
        logger.info("=" * 80)
        
        # Import Pillar 3
        from pillar3_trend_intelligence.trend_scraper import TrendScraper
        from pillar3_trend_intelligence.gemini_analyzer import GeminiTrendAnalyzer
        
        # Scrape trends
        scraper = TrendScraper(
            database_path=os.getenv('DATABASE_PATH')
        )
        
        trends = scraper.scrape_trending_hashtags()
        
        # Analyze trends
        analyzer = GeminiTrendAnalyzer(
            api_key=os.getenv('GEMINI_API_KEY')
        )
        
        analysis = analyzer.analyze_trends(trends)
        
        logger.info("✅ Trend analysis complete")
        return analysis
    
    def run_content_processing(self, raw_video_dir: str):
        """
        Run content processing (Pillar 2).
        
        This processes raw videos into 60 unique TikTok-ready clips.
        
        Args:
            raw_video_dir: Directory containing raw video files
        """
        logger.info("=" * 80)
        logger.info("RUNNING CONTENT PROCESSING (PILLAR 2)")
        logger.info("=" * 80)
        
        # Import Pillar 2
        from pillar2_content_processing.batch_processor import BatchProcessor
        
        # Process videos
        processor = BatchProcessor(
            database_path=os.getenv('DATABASE_PATH')
        )
        
        processor.process_directory(raw_video_dir)
        
        logger.info("✅ Content processing complete")
    
    def run_metadata_generation(self, affilify_feature: str, trends_file: str):
        """
        Run metadata generation (Pillar 4).
        
        This generates 60 unique captions/hashtags for a feature.
        
        Args:
            affilify_feature: The Affilify feature to generate metadata for
            trends_file: Path to trends JSON file
        """
        logger.info("=" * 80)
        logger.info("RUNNING METADATA GENERATION (PILLAR 4)")
        logger.info("=" * 80)
        
        # Import Pillar 4
        from pillar4_content_strategy.metadata_generator import MetadataGenerator
        
        # Generate metadata
        generator = MetadataGenerator(
            api_key=os.getenv('GEMINI_API_KEY')
        )
        
        # Load trends
        import json
        with open(trends_file, 'r') as f:
            trends_data = json.load(f)
        
        trending_hashtags = [h.get('hashtag', '') for h in trends_data.get('hashtags', [])]
        
        # Generate batch
        metadata_batch = generator.generate_batch_metadata(
            affilify_feature=affilify_feature,
            trending_hashtags=trending_hashtags,
            num_variations=60
        )
        
        logger.info("✅ Metadata generation complete")
        return metadata_batch
    
    def run_distribution(self, dry_run: bool = False):
        """
        Run distribution (Pillar 5).
        
        This posts videos to TikTok across all 60 accounts.
        
        Args:
            dry_run: If True, don't actually post
        """
        logger.info("=" * 80)
        logger.info("RUNNING DISTRIBUTION (PILLAR 5)")
        logger.info("=" * 80)
        
        # Import Pillar 5
        from pillar5_distribution.posting_scheduler import PostingScheduler
        
        # Schedule and execute posts
        scheduler = PostingScheduler(
            database_path=os.getenv('DATABASE_PATH')
        )
        
        # Load resources
        profiles = scheduler.load_profiles()
        videos = scheduler.load_processed_videos()
        
        # Create assignments
        # (This is simplified - in reality would load metadata too)
        assignments = scheduler.assign_posts_to_accounts(videos, [], profiles)
        
        # Create schedule
        scheduled_times = scheduler.create_posting_schedule(len(assignments))
        
        # Execute
        scheduler.execute_posting_schedule(assignments, scheduled_times, dry_run=dry_run)
        
        logger.info("✅ Distribution complete")
    
    def run_analytics(self):
        """
        Run analytics (Pillar 6).
        
        This scrapes performance and generates optimization insights.
        """
        logger.info("=" * 80)
        logger.info("RUNNING ANALYTICS (PILLAR 6)")
        logger.info("=" * 80)
        
        # Import Pillar 6
        from pillar6_analytics.performance_scraper import PerformanceScraper
        from pillar6_analytics.optimization_engine import OptimizationEngine
        
        # Scrape performance
        with PerformanceScraper(database_path=os.getenv('DATABASE_PATH')) as scraper:
            # TODO: Load video URLs from database
            video_urls = []
            metrics = scraper.scrape_batch_metrics(video_urls)
        
        # Run optimization
        engine = OptimizationEngine(database_path=os.getenv('DATABASE_PATH'))
        report = engine.generate_optimization_report()
        
        logger.info("✅ Analytics complete")
        return report
    
    def run_reporting(self):
        """
        Run reporting (Pillar 7).
        
        This generates the daily report and video requests.
        """
        logger.info("=" * 80)
        logger.info("RUNNING REPORTING (PILLAR 7)")
        logger.info("=" * 80)
        
        # Import Pillar 7
        from pillar7_reporting.report_generator import ReportGenerator
        
        # Generate report
        generator = ReportGenerator(database_path=os.getenv('DATABASE_PATH'))
        report = generator.generate_full_report()
        
        # Save report
        report_file = generator.save_report(
            report,
            os.getenv('REPORTS_DIR', '/home/ubuntu/affilify_tiktok_system/data/reports')
        )
        
        # Print human-readable version
        text_report = generator.generate_human_readable_report(report)
        print(text_report)
        
        logger.info("✅ Reporting complete")
        return report
    
    def run_daily_workflow(self):
        """
        Run the complete daily workflow.
        
        This is the full Diamond Factory pipeline:
        1. Trend Analysis
        2. Content Processing (if new videos available)
        3. Metadata Generation
        4. Distribution
        5. Analytics
        6. Reporting
        """
        logger.info("=" * 100)
        logger.info("STARTING DAILY WORKFLOW - THE DIAMOND FACTORY")
        logger.info("=" * 100)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Trend Analysis
            self.run_trend_analysis()
            
            # Step 2: Content Processing
            # (Skip if no new videos)
            raw_video_dir = os.getenv('RAW_VIDEO_DIR', '/home/ubuntu/affilify_tiktok_system/data/raw_videos')
            if Path(raw_video_dir).exists() and list(Path(raw_video_dir).glob('*.mp4')):
                self.run_content_processing(raw_video_dir)
            else:
                logger.info("No new raw videos found - skipping content processing")
            
            # Step 3: Metadata Generation
            # (For each feature that has processed videos)
            # TODO: Implement feature detection
            
            # Step 4: Distribution
            self.run_distribution(dry_run=False)
            
            # Step 5: Analytics (wait 24 hours after posting)
            # TODO: Implement time-based execution
            
            # Step 6: Reporting
            self.run_reporting()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("=" * 100)
            logger.info(f"DAILY WORKFLOW COMPLETE - Duration: {duration:.0f} seconds")
            logger.info("=" * 100)
        
        except Exception as e:
            logger.error(f"Daily workflow failed: {e}", exc_info=True)
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Affilify TikTok System - Master Workflow'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Run initial setup (create MultiLogin profiles)'
    )
    
    parser.add_argument(
        '--daily-run',
        action='store_true',
        help='Run the complete daily workflow'
    )
    
    parser.add_argument(
        '--test-pillar',
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7],
        help='Test a specific pillar'
    )
    
    args = parser.parse_args()
    
    # Create logs directory
    Path('/home/ubuntu/affilify_tiktok_system/logs').mkdir(parents=True, exist_ok=True)
    
    # Initialize workflow
    workflow = MasterWorkflow()
    
    if args.setup:
        workflow.run_setup()
    
    elif args.daily_run:
        workflow.run_daily_workflow()
    
    elif args.test_pillar:
        pillar_methods = {
            1: workflow.run_setup,
            3: workflow.run_trend_analysis,
            5: lambda: workflow.run_distribution(dry_run=True),
            6: workflow.run_analytics,
            7: workflow.run_reporting
        }
        
        method = pillar_methods.get(args.test_pillar)
        if method:
            method()
        else:
            logger.error(f"No test method for pillar {args.test_pillar}")
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
