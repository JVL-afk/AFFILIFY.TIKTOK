#!/usr/bin/env python3
"""
Music Integration Script
========================
Adds downloaded background music to video clips.

This script:
1. Reads music recommendations from music_reports/
2. Finds corresponding music files in music/ directory
3. Adds music to video clips
4. Saves final videos ready for posting

Usage:
    python3 add_music_to_clips.py --clips-dir data/batch_output/split --music-dir data/music --output-dir data/final_clips
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional

from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MusicIntegrator:
    """
    Integrates background music with video clips.
    """
    
    def __init__(self, clips_dir: str, music_dir: str, output_dir: str):
        """
        Initialize the music integrator.
        
        Args:
            clips_dir: Directory containing video clips
            music_dir: Directory containing downloaded music files
            output_dir: Directory to save final videos with music
        """
        self.clips_dir = Path(clips_dir)
        self.music_dir = Path(music_dir)
        self.output_dir = Path(output_dir)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MusicIntegrator initialized")
        logger.info(f"  Clips: {self.clips_dir}")
        logger.info(f"  Music: {self.music_dir}")
        logger.info(f"  Output: {self.output_dir}")
    
    def find_music_for_clip(self, clip_name: str) -> Optional[Path]:
        """
        Find the music file for a clip.
        
        Args:
            clip_name: Name of the clip file (e.g., "batch1_video1_clip1.mp4")
        
        Returns:
            Path to music file or None if not found
        """
        # Try to find music file with same base name
        clip_stem = Path(clip_name).stem
        
        # Common audio extensions
        extensions = ['.mp3', '.wav', '.m4a', '.ogg']
        
        for ext in extensions:
            music_path = self.music_dir / f"{clip_stem}{ext}"
            if music_path.exists():
                return music_path
        
        # Try without clip number suffix
        # e.g., "batch1_video1_clip1" -> "batch1_video1"
        if '_clip' in clip_stem:
            base_name = clip_stem.split('_clip')[0]
            for ext in extensions:
                music_path = self.music_dir / f"{base_name}{ext}"
                if music_path.exists():
                    return music_path
        
        return None
    
    def add_music_to_clip(self, 
                          clip_path: Path, 
                          music_path: Path,
                          music_volume: float = 0.3) -> Path:
        """
        Add background music to a video clip.
        
        Args:
            clip_path: Path to video clip
            music_path: Path to music file
            music_volume: Volume of background music (0.0 to 1.0)
        
        Returns:
            Path to output video with music
        """
        logger.info(f"Adding music to: {clip_path.name}")
        logger.info(f"  Music: {music_path.name}")
        
        try:
            # Load video and audio
            video = VideoFileClip(str(clip_path))
            music = AudioFileClip(str(music_path))
            
            # Adjust music duration to match video
            if music.duration > video.duration:
                # Trim music to video length
                music = music.subclipped(0, video.duration)
            elif music.duration < video.duration:
                # Loop music to fill video length
                loops_needed = int(video.duration / music.duration) + 1
                # Concatenate music clips to loop
                music_clips = [music] * loops_needed
                from moviepy import concatenate_audioclips
                music = concatenate_audioclips(music_clips)
                music = music.subclipped(0, video.duration)
            
            # Reduce music volume using audio transformation
            def adjust_volume(get_frame, t):
                return get_frame(t) * music_volume
            
            music = music.transform(adjust_volume)
            
            # Combine original audio with music
            if video.audio:
                final_audio = CompositeAudioClip([video.audio, music])
            else:
                final_audio = music
            
            # Set the audio
            final_video = video.with_audio(final_audio)
            
            # Generate output path
            output_path = self.output_dir / clip_path.name
            
            # Write output
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio-music.m4a',
                remove_temp=True,
                fps=30,
                preset='medium',
                bitrate='8000k',
                logger=None
            )
            
            # Clean up
            video.close()
            music.close()
            final_video.close()
            
            logger.info(f"  ✅ Saved: {output_path.name}")
            return output_path
        
        except Exception as e:
            logger.error(f"  ✗ Failed: {e}")
            raise
    
    def process_all_clips(self, music_volume: float = 0.3) -> Dict[str, any]:
        """
        Process all clips in the clips directory.
        
        Args:
            music_volume: Volume of background music (0.0 to 1.0)
        
        Returns:
            Dictionary with processing results
        """
        # Find all video clips
        clip_files = sorted(self.clips_dir.glob("*.mp4"))
        
        if not clip_files:
            logger.warning(f"No video clips found in {self.clips_dir}")
            return {'total': 0, 'successful': 0, 'failed': 0, 'skipped': 0}
        
        logger.info(f"\n{'='*70}")
        logger.info(f"ADDING MUSIC TO {len(clip_files)} CLIPS")
        logger.info(f"{'='*70}\n")
        
        results = {
            'total': len(clip_files),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'clips': []
        }
        
        for i, clip_path in enumerate(clip_files, 1):
            logger.info(f"[{i}/{len(clip_files)}] Processing: {clip_path.name}")
            
            # Find music for this clip
            music_path = self.find_music_for_clip(clip_path.name)
            
            if not music_path:
                logger.warning(f"  ⚠ No music found, copying without music...")
                # Copy clip without music
                output_path = self.output_dir / clip_path.name
                import shutil
                shutil.copy2(clip_path, output_path)
                results['skipped'] += 1
                results['clips'].append({
                    'clip': str(clip_path),
                    'output': str(output_path),
                    'status': 'no_music',
                    'music': None
                })
                continue
            
            try:
                output_path = self.add_music_to_clip(clip_path, music_path, music_volume)
                results['successful'] += 1
                results['clips'].append({
                    'clip': str(clip_path),
                    'output': str(output_path),
                    'status': 'success',
                    'music': str(music_path)
                })
            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                results['failed'] += 1
                results['clips'].append({
                    'clip': str(clip_path),
                    'output': None,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Print summary
        logger.info(f"\n{'='*70}")
        logger.info(f"MUSIC INTEGRATION COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Total clips: {results['total']}")
        logger.info(f"With music: {results['successful']}")
        logger.info(f"Without music: {results['skipped']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"{'='*70}\n")
        
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Add background music to video clips"
    )
    parser.add_argument(
        '--clips-dir',
        required=True,
        help='Directory containing video clips'
    )
    parser.add_argument(
        '--music-dir',
        required=True,
        help='Directory containing downloaded music files'
    )
    parser.add_argument(
        '--output-dir',
        required=True,
        help='Directory to save final videos with music'
    )
    parser.add_argument(
        '--volume',
        type=float,
        default=0.3,
        help='Music volume (0.0 to 1.0, default: 0.3)'
    )
    
    args = parser.parse_args()
    
    # Create integrator
    integrator = MusicIntegrator(
        clips_dir=args.clips_dir,
        music_dir=args.music_dir,
        output_dir=args.output_dir
    )
    
    # Process all clips
    results = integrator.process_all_clips(music_volume=args.volume)
    
    # Exit with appropriate code
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
