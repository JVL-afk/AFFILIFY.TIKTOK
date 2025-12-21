"""
Pillar 4 Main Script
====================
Main entry point for the Content Strategy and Metadata Generation System.

Usage:
    python main.py --feature "Create Website" --trends-file trends.json
    python main.py --batch --trends-file trends.json
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

from pillar4_content_strategy.metadata_generator import MetadataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# All Affilify features
AFFILIFY_FEATURES = [
    "Create Website",
    "Analyze Website",
    "My Websites",
    "Advanced Analytics",
    "AI Chatbot",
    "A/B Testing",
    "Email Marketing",
    "Team Collaboration",
    "API Management",
    "Custom Integrations",
    "Code Editor",
    "Advanced Reporting"
]


def load_config() -> dict:
    """Load configuration from environment variables."""
    env_path = Path(__file__).parent.parent / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
    
    config = {
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'metadata_output_dir': os.getenv(
            'METADATA_OUTPUT_DIR',
            '/home/ubuntu/affilify_tiktok_system/data/metadata'
        )
    }
    
    return config


def load_trends(trends_file: str) -> List[str]:
    """Load trending hashtags from a trends file."""
    with open(trends_file, 'r') as f:
        trends_data = json.load(f)
    
    # Extract hashtags
    hashtags = [h.get('hashtag', '') for h in trends_data.get('hashtags', [])]
    
    logger.info(f"Loaded {len(hashtags)} trending hashtags from {trends_file}")
    return hashtags


def generate_metadata_for_feature(config: dict, 
                                  feature: str,
                                  trending_hashtags: List[str],
                                  num_variations: int = 60):
    """Generate metadata for a single feature."""
    logger.info(f"Generating metadata for feature: {feature}")
    
    generator = MetadataGenerator(api_key=config['gemini_api_key'])
    
    # Generate batch metadata
    metadata_batch = generator.generate_batch_metadata(
        affilify_feature=feature,
        trending_hashtags=trending_hashtags,
        num_variations=num_variations
    )
    
    # Save to file
    output_dir = Path(config['metadata_output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    feature_safe = feature.replace(" ", "_").lower()
    output_file = output_dir / f"metadata_{feature_safe}_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(metadata_batch, f, indent=2)
    
    logger.info(f"✅ Metadata saved to: {output_file}")
    
    return metadata_batch


def generate_metadata_for_all_features(config: dict, trending_hashtags: List[str]):
    """Generate metadata for all Affilify features."""
    logger.info("=" * 80)
    logger.info("GENERATING METADATA FOR ALL FEATURES")
    logger.info("=" * 80)
    
    all_metadata = {}
    
    for feature in AFFILIFY_FEATURES:
        metadata_batch = generate_metadata_for_feature(
            config=config,
            feature=feature,
            trending_hashtags=trending_hashtags,
            num_variations=60
        )
        
        all_metadata[feature] = metadata_batch
    
    # Save combined file
    output_dir = Path(config['metadata_output_dir'])
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_file = output_dir / f"metadata_all_features_{timestamp}.json"
    
    with open(combined_file, 'w') as f:
        json.dump(all_metadata, f, indent=2)
    
    logger.info("=" * 80)
    logger.info("METADATA GENERATION COMPLETE")
    logger.info(f"  ✅ Features processed: {len(AFFILIFY_FEATURES)}")
    logger.info(f"  ✅ Total variations: {len(AFFILIFY_FEATURES) * 60}")
    logger.info(f"  ✅ Combined file: {combined_file}")
    logger.info("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Affilify Content Strategy System (Pillar 4)'
    )
    
    parser.add_argument(
        '--feature',
        type=str,
        choices=AFFILIFY_FEATURES,
        help='Generate metadata for a specific feature'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Generate metadata for all features'
    )
    
    parser.add_argument(
        '--trends-file',
        type=str,
        required=True,
        help='Path to trends JSON file'
    )
    
    parser.add_argument(
        '--variations',
        type=int,
        default=60,
        help='Number of variations to generate (default: 60)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Load trends
    trending_hashtags = load_trends(args.trends_file)
    
    if args.batch:
        # Generate for all features
        generate_metadata_for_all_features(config, trending_hashtags)
    
    elif args.feature:
        # Generate for single feature
        generate_metadata_for_feature(
            config=config,
            feature=args.feature,
            trending_hashtags=trending_hashtags,
            num_variations=args.variations
        )
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
