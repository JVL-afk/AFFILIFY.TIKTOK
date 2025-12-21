"""
Pillar 3 Main Script
====================
Main entry point for the Trend Forecasting and Intelligence System.

Usage:
    python main.py --scrape
    python main.py --analyze
    python main.py --full
"""

import os
import sys
import logging
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pillar3_trend_intelligence.trend_scraper import TikTokTrendScraper
from pillar3_trend_intelligence.gemini_analyzer import GeminiTrendAnalyzer

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
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'trends_output_dir': os.getenv(
            'TRENDS_OUTPUT_DIR',
            '/home/ubuntu/affilify_tiktok_system/data/trends'
        )
    }
    
    return config


def scrape_trends(config: dict):
    """Scrape current TikTok trends."""
    logger.info("Starting trend scraping...")
    
    with TikTokTrendScraper(
        database_path=config['database_path'],
        headless=True
    ) as scraper:
        # Scrape all trends
        trends = scraper.scrape_all_trends()
        
        # Save to database
        scraper.save_trends_to_database(trends)
        
        return trends


def analyze_trends(config: dict, trends: dict):
    """Analyze trends with Gemini AI."""
    logger.info("Starting trend analysis...")
    
    analyzer = GeminiTrendAnalyzer(api_key=config['gemini_api_key'])
    
    # Generate basic strategy
    strategy = analyzer.generate_content_strategy(trends)
    
    logger.info("Content Strategy Generated:")
    logger.info(json.dumps(strategy, indent=2))
    
    # Generate advanced strategy with Gemini (if API key available)
    if config['gemini_api_key']:
        logger.info("Generating advanced strategy with Gemini AI...")
        advanced_strategy = analyzer.generate_advanced_strategy_with_gemini(trends)
        
        logger.info("=" * 80)
        logger.info("GEMINI ADVANCED STRATEGY:")
        logger.info("=" * 80)
        logger.info(advanced_strategy)
        logger.info("=" * 80)
        
        strategy['gemini_analysis'] = advanced_strategy
    
    # Save strategy
    output_dir = Path(config['trends_output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    strategy_file = output_dir / f"strategy_{timestamp}.json"
    
    with open(strategy_file, 'w') as f:
        json.dump(strategy, f, indent=2)
    
    logger.info(f"✅ Strategy saved to: {strategy_file}")
    
    return strategy


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Affilify Trend Intelligence System (Pillar 3)'
    )
    
    parser.add_argument(
        '--scrape',
        action='store_true',
        help='Scrape current TikTok trends'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze existing trend data'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Run full pipeline (scrape + analyze)'
    )
    
    parser.add_argument(
        '--trends-file',
        type=str,
        help='Path to existing trends JSON file (for analyze mode)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if args.full or args.scrape:
        # Scrape trends
        trends = scrape_trends(config)
        
        if args.full:
            # Also analyze
            analyze_trends(config, trends)
    
    elif args.analyze:
        # Load trends from file
        if not args.trends_file:
            logger.error("--trends-file required for analyze mode")
            sys.exit(1)
        
        with open(args.trends_file, 'r') as f:
            trends = json.load(f)
        
        analyze_trends(config, trends)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
