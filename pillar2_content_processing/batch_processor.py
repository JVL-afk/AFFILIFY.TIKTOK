"""
Batch Content Processor
=======================
This module orchestrates the processing of raw videos into 60+ unique,
optimized TikTok-ready videos.

Workflow:
1. Load raw video from input directory
2. Convert to 9:16 TikTok format
3. Optionally split into multiple clips
4. Add feature-specific text overlays
5. Generate 60+ unique variations (one per account)
6. Store metadata in database
7. Verify uniqueness via file hashing

This ensures each account posts truly unique content.
"""

import os
import sys
import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pillar2_content_processing.video_processor import VideoProcessor, VideoProcessingError
from shared.database import Database

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Orchestrates batch processing of videos for distribution.
    
    This class handles the complete workflow from raw video input
    to 60+ unique, optimized outputs ready for posting.
    """
    
    # Affilify features (from the 12 features we researched)
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
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the batch processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize components
        self.video_processor = VideoProcessor(
            output_dir=config['processed_video_output_dir']
        )
        
        self.database = Database(config['database_path'])
        
        # Create directories
        self.raw_input_dir = Path(config['raw_video_input_dir'])
        self.raw_input_dir.mkdir(parents=True, exist_ok=True)
        
        self.processed_output_dir = Path(config['processed_video_output_dir'])
        self.processed_output_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_dir = Path(config.get('temp_dir', '/tmp/affilify_processing'))
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("BatchProcessor initialized")
    
    def process_raw_video(self, raw_video_path: str,
                         affilify_feature: str,
                         num_variations: int = 60,
                         add_text_overlay: bool = True,
                         split_into_clips: bool = False,
                         clip_duration: int = 30) -> Dict[str, Any]:
        """
        Process a raw video into multiple unique variations.
        
        Args:
            raw_video_path: Path to the raw input video
            affilify_feature: Which Affilify feature this video demonstrates
            num_variations: Number of unique variations to create
            add_text_overlay: Whether to add text overlay
            split_into_clips: Whether to split the video first
            clip_duration: Duration of each clip if splitting
        
        Returns:
            Dictionary containing processing results
        
        Raises:
            VideoProcessingError: If processing fails
        """
        logger.info("=" * 80)
        logger.info(f"Processing raw video: {raw_video_path}")
        logger.info(f"Feature: {affilify_feature}")
        logger.info(f"Variations to create: {num_variations}")
        logger.info("=" * 80)
        
        results = {
            'raw_video_path': raw_video_path,
            'affilify_feature': affilify_feature,
            'num_variations': num_variations,
            'processed_videos': [],
            'failed_variations': [],
            'unique_hashes': set(),
            'started_at': datetime.now().isoformat(),
            'completed_at': None
        }
        
        try:
            # Step 1: Convert to TikTok format
            logger.info("Step 1: Converting to TikTok format (9:16)...")
            tiktok_video = self.video_processor.convert_to_tiktok_format(
                input_path=raw_video_path,
                output_path=str(self.temp_dir / f"tiktok_format_{Path(raw_video_path).stem}.mp4"),
                crop_method="center"
            )
            logger.info(f"✅ Converted to TikTok format: {tiktok_video}")
            
            # Step 2: Optionally split into clips
            base_videos = [tiktok_video]
            
            if split_into_clips:
                logger.info(f"Step 2: Splitting into {clip_duration}s clips...")
                clips = self.video_processor.split_video(
                    input_path=tiktok_video,
                    clip_duration=clip_duration,
                    max_clips=num_variations
                )
                base_videos = clips
                logger.info(f"✅ Created {len(clips)} clips")
            else:
                logger.info("Step 2: Skipping splitting (using full video)")
            
            # Step 3: Add text overlay (if requested)
            if add_text_overlay:
                logger.info("Step 3: Adding text overlays...")
                overlay_text = f"✨ {affilify_feature} ✨"
                
                overlayed_videos = []
                for i, base_video in enumerate(base_videos):
                    overlay_output = str(self.temp_dir / f"overlay_{i}_{Path(base_video).stem}.mp4")
                    
                    overlayed = self.video_processor.add_text_overlay(
                        input_path=base_video,
                        text=overlay_text,
                        position=("center", "top"),
                        font_size=60,
                        font_color="white",
                        bg_color="black",
                        bg_opacity=0.7,
                        output_path=overlay_output
                    )
                    overlayed_videos.append(overlayed)
                
                base_videos = overlayed_videos
                logger.info(f"✅ Added text overlays to {len(base_videos)} videos")
            else:
                logger.info("Step 3: Skipping text overlay")
            
            # Step 4: Generate unique variations
            logger.info(f"Step 4: Generating {num_variations} unique variations...")
            
            # Determine how many variations per base video
            variations_per_base = max(1, num_variations // len(base_videos))
            
            variation_count = 0
            for base_idx, base_video in enumerate(base_videos):
                # Calculate how many variations for this base
                remaining = num_variations - variation_count
                variations_to_create = min(variations_per_base, remaining)
                
                if variations_to_create == 0:
                    break
                
                logger.info(f"Creating {variations_to_create} variations from base video {base_idx + 1}/{len(base_videos)}")
                
                for var_idx in range(variations_to_create):
                    try:
                        variation_path = self.video_processor.generate_unique_variation(
                            input_path=base_video,
                            variation_index=variation_count,
                            total_variations=num_variations
                        )
                        
                        # Calculate hash to verify uniqueness
                        file_hash = self.video_processor.calculate_file_hash(variation_path)
                        
                        # Check for duplicates
                        if file_hash in results['unique_hashes']:
                            logger.warning(f"⚠️  Duplicate hash detected for variation {variation_count + 1}")
                        
                        results['unique_hashes'].add(file_hash)
                        
                        # Get video info
                        video_info = self.video_processor.get_video_info(variation_path)
                        
                        # Store result
                        results['processed_videos'].append({
                            'variation_index': variation_count,
                            'file_path': variation_path,
                            'file_hash': file_hash,
                            'file_size_mb': video_info.get('file_size_mb', 0),
                            'duration': video_info.get('duration', 0),
                            'base_video_index': base_idx
                        })
                        
                        variation_count += 1
                        
                        if variation_count % 10 == 0:
                            logger.info(f"Progress: {variation_count}/{num_variations} variations created")
                    
                    except Exception as e:
                        logger.error(f"Failed to create variation {variation_count}: {e}")
                        results['failed_variations'].append({
                            'variation_index': variation_count,
                            'error': str(e)
                        })
                        variation_count += 1
            
            logger.info(f"✅ Created {len(results['processed_videos'])} unique variations")
            
            # Step 5: Verify uniqueness
            logger.info("Step 5: Verifying uniqueness...")
            unique_count = len(results['unique_hashes'])
            total_count = len(results['processed_videos'])
            
            if unique_count == total_count:
                logger.info(f"✅ All {total_count} videos are unique")
            else:
                logger.warning(f"⚠️  Only {unique_count}/{total_count} videos are unique")
            
            results['completed_at'] = datetime.now().isoformat()
            results['success'] = True
            
            # Step 6: Save processing manifest
            self._save_processing_manifest(results)
            
            logger.info("=" * 80)
            logger.info("BATCH PROCESSING COMPLETE")
            logger.info(f"  ✅ Successful: {len(results['processed_videos'])}")
            logger.info(f"  ❌ Failed: {len(results['failed_variations'])}")
            logger.info(f"  🔒 Unique hashes: {len(results['unique_hashes'])}")
            logger.info("=" * 80)
            
            return results
        
        except Exception as e:
            logger.error(f"Batch processing failed: {e}", exc_info=True)
            results['success'] = False
            results['error'] = str(e)
            results['completed_at'] = datetime.now().isoformat()
            return results
    
    def _save_processing_manifest(self, results: Dict[str, Any]):
        """
        Save a processing manifest to disk.
        
        Args:
            results: Processing results dictionary
        """
        # Convert set to list for JSON serialization
        results_copy = results.copy()
        results_copy['unique_hashes'] = list(results_copy['unique_hashes'])
        
        # Generate manifest filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        feature_slug = results['affilify_feature'].lower().replace(' ', '_')
        manifest_path = self.processed_output_dir / f"manifest_{feature_slug}_{timestamp}.json"
        
        # Save manifest
        with open(manifest_path, 'w') as f:
            json.dump(results_copy, f, indent=2)
        
        logger.info(f"Saved processing manifest: {manifest_path}")
    
    def get_next_unprocessed_video(self) -> Optional[str]:
        """
        Get the next unprocessed video from the raw input directory.
        
        Returns:
            Path to the next video to process, or None if none available
        """
        # Get all video files in the raw input directory
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        
        for file_path in self.raw_input_dir.iterdir():
            if file_path.suffix.lower() in video_extensions:
                # Check if this video has been processed
                # (Simple check: look for a manifest file with this video name)
                video_stem = file_path.stem
                manifests = list(self.processed_output_dir.glob(f"manifest_*{video_stem}*.json"))
                
                if not manifests:
                    return str(file_path)
        
        return None
    
    def process_all_pending_videos(self, num_variations_per_video: int = 60):
        """
        Process all pending videos in the raw input directory.
        
        Args:
            num_variations_per_video: Number of variations to create per video
        """
        logger.info("Processing all pending videos...")
        
        processed_count = 0
        
        while True:
            next_video = self.get_next_unprocessed_video()
            
            if next_video is None:
                logger.info("No more videos to process")
                break
            
            # Try to infer the feature from the filename
            video_name = Path(next_video).stem.lower()
            
            feature = None
            for affilify_feature in self.AFFILIFY_FEATURES:
                feature_slug = affilify_feature.lower().replace(' ', '_')
                if feature_slug in video_name:
                    feature = affilify_feature
                    break
            
            if feature is None:
                logger.warning(f"Could not infer feature from filename: {video_name}")
                logger.warning("Skipping this video. Please rename it to include the feature name.")
                # Move to a "needs_review" folder
                needs_review_dir = self.raw_input_dir / "needs_review"
                needs_review_dir.mkdir(exist_ok=True)
                Path(next_video).rename(needs_review_dir / Path(next_video).name)
                continue
            
            # Process the video
            try:
                results = self.process_raw_video(
                    raw_video_path=next_video,
                    affilify_feature=feature,
                    num_variations=num_variations_per_video,
                    add_text_overlay=True,
                    split_into_clips=False
                )
                
                if results['success']:
                    processed_count += 1
                    logger.info(f"✅ Successfully processed video {processed_count}")
                else:
                    logger.error(f"❌ Failed to process video: {results.get('error')}")
            
            except Exception as e:
                logger.error(f"Error processing video {next_video}: {e}", exc_info=True)
        
        logger.info(f"Batch processing complete. Processed {processed_count} videos.")


if __name__ == "__main__":
    # Test the batch processor
    logging.basicConfig(level=logging.INFO)
    
    print("BatchProcessor module loaded successfully!")
    print("=" * 80)
    print("This module orchestrates batch video processing for the Affilify system.")
    print("=" * 80)
