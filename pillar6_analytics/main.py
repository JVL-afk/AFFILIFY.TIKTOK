"""
Pillar 6 Main Script
====================
Main entry point for the Analytics and Optimization System.

Usage:
    python main.py --scrape
    python main.py --optimize
    python main.py --full-analysis
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pillar6_analytics.performance_scraper import PerformanceScraper
from pillar6_analytics.optimization_engine import OptimizationEngine

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


def scrape_performance(config: dict):
    """Scrape performance metrics for all posted videos."""
    logger.info("Starting performance scraping...")
    
    # TODO: Load video URLs from database
    video_urls = []
    
    if not video_urls:
        logger.warning("No video URLs found in database")
        return
    
    with PerformanceScraper(database_path=config['database_path']) as scraper:
        metrics = scraper.scrape_batch_metrics(video_urls)
        
        # TODO: Save metrics to database
        logger.info(f"✅ Scraped metrics for {len(metrics)} videos")


def run_optimization(config: dict):
    """Run optimization analysis and generate report."""
    logger.info("Starting optimization analysis...")
    
    engine = OptimizationEngine(database_path=config['database_path'])
    
    report = engine.generate_optimization_report()
    
    report_file = engine.save_report(report, config['reports_dir'])
    
    logger.info(f"✅ Optimization report generated: {report_file}")
    
    # Print key recommendations
    logger.info("\nKEY RECOMMENDATIONS:")
    for idx, rec in enumerate(report['recommendations'], 1):
        logger.info(f"  {idx}. {rec}")


def run_full_analysis(config: dict):
    """Run complete analysis pipeline."""
    logger.info("=" * 80)
    logger.info("RUNNING FULL ANALYSIS PIPELINE")
    logger.info("=" * 80)
    
    # Step 1: Scrape performance
    scrape_performance(config)
    
    # Step 2: Run optimization
    run_optimization(config)
    
    logger.info("=" * 80)
    logger.info("FULL ANALYSIS COMPLETE")
    logger.info("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Affilify Analytics System (Pillar 6)'
    )
    
    parser.add_argument(
        '--scrape',
        action='store_true',
        help='Scrape performance metrics'
    )
    
    parser.add_argument(
        '--optimize',
        action='store_true',
        help='Run optimization analysis'
    )
    
    parser.add_argument(
        '--full-analysis',
        action='store_true',
        help='Run complete analysis pipeline'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if args.scrape:
        scrape_performance(config)
    
    elif args.optimize:
        run_optimization(config)
    
    elif args.full_analysis:
        run_full_analysis(config)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
