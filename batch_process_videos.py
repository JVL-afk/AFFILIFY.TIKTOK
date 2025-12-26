#!/usr/bin/env python3
"""
Batch Video Processing Script
==============================
Processes videos in batches of 5 with 1-hour breaks between batches.

This script:
1. Takes your 45 videos
2. Processes them in batches of 5
3. Applies viral editing, music selection, and caption generation
4. Waits 1 hour between batches
5. Prepares everything for posting

Usage:
    python3 batch_process_videos.py --input-dir data/raw_videos --batch-size 5 --break-minutes 60
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pillar2_content_processing.video_processor import VideoProcessor
from pillar2_content_processing.music_selector import MusicSelector
from pillar4_content_strategy.viral_caption_generator import ViralCaptionGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchVideoProcessor:
    """
    Processes videos in batches with breaks between batches.
    """
    
    def __init__(self,
                 input_dir: str,
                 output_dir: str,
                 batch_size: int = 5,
                 break_minutes: int = 60):
        """
        Initialize the batch processor.
        
        Args:
            input_dir: Directory containing raw videos
            output_dir: Directory for processed videos
            batch_size: Number of videos per batch
            break_minutes: Minutes to wait between batches
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.batch_size = batch_size
        self.break_minutes = break_minutes
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "processed").mkdir(exist_ok=True)
        (self.output_dir / "captions").mkdir(exist_ok=True)
        (self.output_dir / "music_reports").mkdir(exist_ok=True)
        
        # Initialize processors
        self.video_processor = VideoProcessor(str(self.output_dir / "processed"))
        self.music_selector = MusicSelector()
        self.caption_generator = ViralCaptionGenerator()
        
        logger.info(f"BatchVideoProcessor initialized")
        logger.info(f"  Input: {self.input_dir}")
        logger.info(f"  Output: {self.output_dir}")
        logger.info(f"  Batch size: {self.batch_size}")
        logger.info(f"  Break: {self.break_minutes} minutes")
    
    def get_video_files(self) -> List[Path]:
        """
        Get all video files from input directory.
        
        Returns:
            List of video file paths
        """
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(self.input_dir.glob(f'*{ext}'))
            video_files.extend(self.input_dir.glob(f'*{ext.upper()}'))
        
        video_files.sort()
        logger.info(f"Found {len(video_files)} video files")
        return video_files
    
    def create_batches(self, video_files: List[Path]) -> List[List[Path]]:
        """
        Split video files into batches.
        
        Args:
            video_files: List of video file paths
        
        Returns:
            List of batches (each batch is a list of paths)
        """
        batches = []
        for i in range(0, len(video_files), self.batch_size):
            batch = video_files[i:i + self.batch_size]
            batches.append(batch)
        
        logger.info(f"Created {len(batches)} batches")
        return batches
    
    def process_video(self, video_path: Path, batch_num: int, video_num: int) -> dict:
        """
        Process a single video.
        
        Args:
            video_path: Path to video file
            batch_num: Batch number
            video_num: Video number within batch
        
        Returns:
            Dictionary with processing results
        """
        logger.info(f"  Processing: {video_path.name}")
        
        try:
            # 1. Convert to TikTok format (9:16, 1080x1920)
            logger.info(f"    Converting to TikTok format...")
            output_name = f"batch{batch_num}_video{video_num}_{video_path.stem}.mp4"
            processed_path = self.video_processor.convert_to_tiktok_format(
                str(video_path),
                output_name
            )
            
            # 2. Generate caption
            logger.info(f"    Generating viral caption...")
            video_description = f"AFFILIFY AI website builder demo - {video_path.stem}"
            caption = self.caption_generator.generate_viral_caption(
                video_description,
                hook_type=None,  # Random hook type
                include_question=(video_num % 3 == 0)  # Every 3rd video has question
            )
            
            # Save caption
            caption_file = self.output_dir / "captions" / f"{output_name}.txt"
            with open(caption_file, 'w', encoding='utf-8') as f:
                f.write(caption['full_caption'])
            
            # 3. Select music
            logger.info(f"    Selecting trending music...")
            music_rec = self.music_selector.find_royalty_free_match(video_description)
            
            # Save music recommendation
            music_file = self.output_dir / "music_reports" / f"{output_name}_music.txt"
            with open(music_file, 'w', encoding='utf-8') as f:
                if music_rec.get('recommendations'):
                    track = music_rec['recommendations'][0]
                    f.write(f"MUSIC RECOMMENDATION\n")
                    f.write(f"=" * 60 + "\n")
                    f.write(f"Title: {track.get('title', 'N/A')}\n")
                    f.write(f"Artist: {track.get('artist', 'N/A')}\n")
                    f.write(f"Source: {track.get('source', 'N/A')}\n")
                    f.write(f"Style: {track.get('style', 'N/A')}\n")
                    f.write(f"Search: {track.get('search_keywords', 'N/A')}\n")
                    f.write(f"Link: {track.get('link', 'N/A')}\n")
            
            logger.info(f"    ✅ Processed successfully!")
            
            return {
                'status': 'success',
                'input_path': str(video_path),
                'output_path': processed_path,
                'caption_file': str(caption_file),
                'music_file': str(music_file),
                'caption': caption,
                'music': music_rec
            }
        
        except Exception as e:
            logger.error(f"    ✗ Failed: {e}")
            return {
                'status': 'failed',
                'input_path': str(video_path),
                'error': str(e)
            }
    
    def process_batch(self, batch: List[Path], batch_num: int) -> List[dict]:
        """
        Process a batch of videos.
        
        Args:
            batch: List of video paths
            batch_num: Batch number
        
        Returns:
            List of processing results
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"PROCESSING BATCH {batch_num}")
        logger.info(f"{'='*70}")
        logger.info(f"Videos in batch: {len(batch)}")
        
        results = []
        for i, video_path in enumerate(batch, 1):
            result = self.process_video(video_path, batch_num, i)
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'failed')
        
        logger.info(f"\nBatch {batch_num} Summary:")
        logger.info(f"  ✅ Successful: {successful}")
        logger.info(f"  ✗ Failed: {failed}")
        
        return results
    
    def wait_between_batches(self, batch_num: int, total_batches: int):
        """
        Wait between batches with countdown.
        
        Args:
            batch_num: Current batch number
            total_batches: Total number of batches
        """
        if batch_num >= total_batches:
            return  # Don't wait after last batch
        
        logger.info(f"\n{'='*70}")
        logger.info(f"BREAK TIME - Waiting {self.break_minutes} minutes before next batch")
        logger.info(f"{'='*70}")
        
        end_time = datetime.now() + timedelta(minutes=self.break_minutes)
        logger.info(f"Next batch starts at: {end_time.strftime('%H:%M:%S')}")
        
        # Wait with periodic updates
        total_seconds = self.break_minutes * 60
        update_interval = 300  # Update every 5 minutes
        
        for elapsed in range(0, total_seconds, update_interval):
            time.sleep(min(update_interval, total_seconds - elapsed))
            remaining = total_seconds - elapsed - update_interval
            if remaining > 0:
                logger.info(f"  ⏰ {remaining // 60} minutes remaining...")
        
        logger.info(f"✅ Break complete! Starting next batch...")
    
    def generate_summary_report(self, all_results: List[List[dict]]) -> str:
        """
        Generate a summary report of all processing.
        
        Args:
            all_results: List of batch results
        
        Returns:
            Path to summary report
        """
        report_path = self.output_dir / "processing_summary.txt"
        
        total_videos = sum(len(batch) for batch in all_results)
        total_successful = sum(
            sum(1 for r in batch if r['status'] == 'success')
            for batch in all_results
        )
        total_failed = total_videos - total_successful
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BATCH VIDEO PROCESSING SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n")
            f.write(f"OVERALL STATISTICS\n")
            f.write(f"-" * 80 + "\n")
            f.write(f"Total videos processed: {total_videos}\n")
            f.write(f"Successful: {total_successful}\n")
            f.write(f"Failed: {total_failed}\n")
            f.write(f"Success rate: {(total_successful/total_videos*100):.1f}%\n")
            f.write(f"\n")
            f.write(f"BATCH BREAKDOWN\n")
            f.write(f"-" * 80 + "\n")
            
            for batch_num, batch_results in enumerate(all_results, 1):
                successful = sum(1 for r in batch_results if r['status'] == 'success')
                failed = len(batch_results) - successful
                f.write(f"\nBatch {batch_num}:\n")
                f.write(f"  Videos: {len(batch_results)}\n")
                f.write(f"  Successful: {successful}\n")
                f.write(f"  Failed: {failed}\n")
                
                # List failed videos
                failed_videos = [r for r in batch_results if r['status'] == 'failed']
                if failed_videos:
                    f.write(f"  Failed videos:\n")
                    for r in failed_videos:
                        f.write(f"    - {Path(r['input_path']).name}: {r['error']}\n")
            
            f.write(f"\n")
            f.write(f"OUTPUT LOCATIONS\n")
            f.write(f"-" * 80 + "\n")
            f.write(f"Processed videos: {self.output_dir / 'processed'}\n")
            f.write(f"Captions: {self.output_dir / 'captions'}\n")
            f.write(f"Music recommendations: {self.output_dir / 'music_reports'}\n")
            f.write(f"\n")
            f.write(f"=" * 80 + "\n")
            f.write(f"NEXT STEPS\n")
            f.write(f"=" * 80 + "\n")
            f.write(f"1. Review processed videos in: {self.output_dir / 'processed'}\n")
            f.write(f"2. Check captions in: {self.output_dir / 'captions'}\n")
            f.write(f"3. Download music from recommendations\n")
            f.write(f"4. Run posting script to upload to TikTok\n")
            f.write(f"\n")
        
        logger.info(f"\n📊 Summary report saved to: {report_path}")
        return str(report_path)
    
    def run(self):
        """
        Execute the complete batch processing workflow.
        """
        logger.info("\n" + "=" * 70)
        logger.info("BATCH VIDEO PROCESSING - STARTING")
        logger.info("=" * 70)
        
        try:
            # Get all video files
            video_files = self.get_video_files()
            
            if not video_files:
                logger.error("No video files found!")
                return False
            
            # Create batches
            batches = self.create_batches(video_files)
            
            # Process each batch
            all_results = []
            for batch_num, batch in enumerate(batches, 1):
                # Process batch
                batch_results = self.process_batch(batch, batch_num)
                all_results.append(batch_results)
                
                # Wait between batches (except after last batch)
                if batch_num < len(batches):
                    self.wait_between_batches(batch_num, len(batches))
            
            # Generate summary report
            self.generate_summary_report(all_results)
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ BATCH PROCESSING COMPLETE!")
            logger.info("=" * 70)
            
            return True
        
        except Exception as e:
            logger.error(f"Batch processing failed: {e}", exc_info=True)
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process videos in batches with breaks between batches"
    )
    parser.add_argument(
        '--input-dir',
        default='data/raw_videos',
        help='Directory containing raw videos'
    )
    parser.add_argument(
        '--output-dir',
        default='data/batch_output',
        help='Directory for processed videos'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=5,
        help='Number of videos per batch (default: 5)'
    )
    parser.add_argument(
        '--break-minutes',
        type=int,
        default=60,
        help='Minutes to wait between batches (default: 60)'
    )
    
    args = parser.parse_args()
    
    # Create and run processor
    processor = BatchVideoProcessor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        break_minutes=args.break_minutes
    )
    
    success = processor.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
