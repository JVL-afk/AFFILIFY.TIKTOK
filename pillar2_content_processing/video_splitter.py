#!/usr/bin/env python3
"""
Smart Video Splitter
====================
Splits long videos into short, viral-optimized TikTok clips.

This module creates 2 clips from each video:
- Clip 1: First 10 seconds + Last 20 seconds (30s total) - "Hook + Finale"
- Clip 2: Last 30 seconds (30s total) - "The Payoff"

This ensures:
1. Every clip is under 30 seconds (TikTok algorithm loves this!)
2. Viewers see the hook AND the conclusion
3. Maximum engagement and watch-through rate
4. Each video becomes 2x the content!

Usage:
    from video_splitter import VideoSplitter
    
    splitter = VideoSplitter()
    clips = splitter.split_video('input.mp4', 'output_dir/')
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from moviepy import VideoFileClip, concatenate_videoclips

logger = logging.getLogger(__name__)


class VideoSplitter:
    """
    Splits videos into short, viral-optimized clips.
    """
    
    # Clip configurations (in seconds)
    CLIP1_INTRO_DURATION = 10   # First 10 seconds
    CLIP1_OUTRO_DURATION = 20   # Last 20 seconds
    CLIP2_DURATION = 30          # Last 30 seconds
    
    def __init__(self, output_dir: str = 'data/split_videos'):
        """
        Initialize the video splitter.
        
        Args:
            output_dir: Directory to save split videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"VideoSplitter initialized with output dir: {self.output_dir}")
    
    def split_video(self, input_path: str, base_name: str = None) -> List[Dict[str, str]]:
        """
        Split a video into 2 viral clips.
        
        Args:
            input_path: Path to input video
            base_name: Base name for output files (auto-generated if None)
        
        Returns:
            List of dictionaries with clip information:
            [
                {
                    'clip_number': 1,
                    'path': '/path/to/clip1.mp4',
                    'duration': 30.0,
                    'description': 'Hook + Finale (First 10s + Last 20s)'
                },
                {
                    'clip_number': 2,
                    'path': '/path/to/clip2.mp4',
                    'duration': 30.0,
                    'description': 'The Payoff (Last 30s)'
                }
            ]
        """
        logger.info(f"Splitting video: {input_path}")
        
        try:
            # Load video
            video = VideoFileClip(input_path)
            duration = video.duration
            
            logger.info(f"Video duration: {duration:.2f}s")
            
            # Generate base name if not provided
            if base_name is None:
                base_name = Path(input_path).stem
            
            clips_info = []
            
            # CLIP 1: First 10 seconds + Last 20 seconds (30s total)
            clip1_path = self.output_dir / f"{base_name}_clip1_hook_finale.mp4"
            clip1 = self._create_clip1(video, duration)
            
            if clip1:
                clip1.write_videofile(
                    str(clip1_path),
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio-clip1.m4a',
                    remove_temp=True,
                    fps=30,
                    preset='medium',
                    bitrate='8000k',
                    logger=None  # Suppress moviepy logs
                )
                clip1.close()
                
                clips_info.append({
                    'clip_number': 1,
                    'path': str(clip1_path),
                    'duration': clip1.duration,
                    'description': 'Hook + Finale (First 10s + Last 20s)',
                    'strategy': 'Grabs attention with hook, delivers conclusion'
                })
                logger.info(f"✅ Clip 1 created: {clip1_path}")
            
            # CLIP 2: Last 30 seconds (30s total)
            clip2_path = self.output_dir / f"{base_name}_clip2_payoff.mp4"
            clip2 = self._create_clip2(video, duration)
            
            if clip2:
                clip2.write_videofile(
                    str(clip2_path),
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio-clip2.m4a',
                    remove_temp=True,
                    fps=30,
                    preset='medium',
                    bitrate='8000k',
                    logger=None  # Suppress moviepy logs
                )
                clip2.close()
                
                clips_info.append({
                    'clip_number': 2,
                    'path': str(clip2_path),
                    'duration': clip2.duration,
                    'description': 'The Payoff (Last 30s)',
                    'strategy': 'Shows the result, CTA, and value proposition'
                })
                logger.info(f"✅ Clip 2 created: {clip2_path}")
            
            # Clean up original video
            video.close()
            
            logger.info(f"✅ Successfully split video into {len(clips_info)} clips")
            return clips_info
        
        except Exception as e:
            logger.error(f"Failed to split video: {e}", exc_info=True)
            return []
    
    def _create_clip1(self, video: VideoFileClip, duration: float) -> VideoFileClip:
        """
        Create Clip 1: First 10 seconds + Last 20 seconds.
        
        Args:
            video: Input video clip
            duration: Video duration in seconds
        
        Returns:
            Combined clip or None if video is too short
        """
        if duration < 30:
            # Video is shorter than 30 seconds, just use the whole thing
            logger.warning(f"Video is only {duration:.2f}s, using entire video for Clip 1")
            return video.subclipped(0, duration)
        
        # Extract first 10 seconds
        intro = video.subclipped(0, min(self.CLIP1_INTRO_DURATION, duration))
        
        # Extract last 20 seconds
        outro_start = max(0, duration - self.CLIP1_OUTRO_DURATION)
        outro = video.subclipped(outro_start, duration)
        
        # Concatenate intro + outro
        combined = concatenate_videoclips([intro, outro], method="compose")
        
        logger.debug(f"Clip 1: {intro.duration:.2f}s intro + {outro.duration:.2f}s outro = {combined.duration:.2f}s total")
        
        return combined
    
    def _create_clip2(self, video: VideoFileClip, duration: float) -> VideoFileClip:
        """
        Create Clip 2: Last 30 seconds.
        
        Args:
            video: Input video clip
            duration: Video duration in seconds
        
        Returns:
            Clip of last 30 seconds or None if video is too short
        """
        if duration < 30:
            # Video is shorter than 30 seconds, skip this clip (already covered by Clip 1)
            logger.warning(f"Video is only {duration:.2f}s, skipping Clip 2 (would be duplicate)")
            return None
        
        # Extract last 30 seconds
        start_time = max(0, duration - self.CLIP2_DURATION)
        clip = video.subclipped(start_time, duration)
        
        logger.debug(f"Clip 2: Last {clip.duration:.2f}s of video")
        
        return clip
    
    def split_video_custom(self, 
                          input_path: str,
                          clip1_segments: List[Tuple[float, float]],
                          clip2_segments: List[Tuple[float, float]],
                          base_name: str = None) -> List[Dict[str, str]]:
        """
        Split video with custom time segments.
        
        Args:
            input_path: Path to input video
            clip1_segments: List of (start, end) tuples for clip 1
            clip2_segments: List of (start, end) tuples for clip 2
            base_name: Base name for output files
        
        Returns:
            List of clip information dictionaries
        """
        logger.info(f"Splitting video with custom segments: {input_path}")
        
        try:
            video = VideoFileClip(input_path)
            
            if base_name is None:
                base_name = Path(input_path).stem
            
            clips_info = []
            
            # Create Clip 1 from segments
            if clip1_segments:
                clip1_parts = [video.subclipped(start, end) for start, end in clip1_segments]
                clip1 = concatenate_videoclips(clip1_parts, method="compose")
                
                clip1_path = self.output_dir / f"{base_name}_clip1_custom.mp4"
                clip1.write_videofile(
                    str(clip1_path),
                    codec='libx264',
                    audio_codec='aac',
                    fps=30,
                    preset='medium',
                    bitrate='8000k',
                    logger=None
                )
                clip1.close()
                
                clips_info.append({
                    'clip_number': 1,
                    'path': str(clip1_path),
                    'duration': sum(end - start for start, end in clip1_segments),
                    'description': f'Custom segments: {clip1_segments}'
                })
            
            # Create Clip 2 from segments
            if clip2_segments:
                clip2_parts = [video.subclipped(start, end) for start, end in clip2_segments]
                clip2 = concatenate_videoclips(clip2_parts, method="compose")
                
                clip2_path = self.output_dir / f"{base_name}_clip2_custom.mp4"
                clip2.write_videofile(
                    str(clip2_path),
                    codec='libx264',
                    audio_codec='aac',
                    fps=30,
                    preset='medium',
                    bitrate='8000k',
                    logger=None
                )
                clip2.close()
                
                clips_info.append({
                    'clip_number': 2,
                    'path': str(clip2_path),
                    'duration': sum(end - start for start, end in clip2_segments),
                    'description': f'Custom segments: {clip2_segments}'
                })
            
            video.close()
            
            return clips_info
        
        except Exception as e:
            logger.error(f"Failed to split video with custom segments: {e}", exc_info=True)
            return []


def main():
    """Test the video splitter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Split videos into viral TikTok clips")
    parser.add_argument('input', help='Input video file')
    parser.add_argument('--output-dir', default='data/split_videos', help='Output directory')
    parser.add_argument('--base-name', help='Base name for output files')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Split video
    splitter = VideoSplitter(output_dir=args.output_dir)
    clips = splitter.split_video(args.input, base_name=args.base_name)
    
    # Print results
    print("\n" + "=" * 70)
    print("VIDEO SPLITTING COMPLETE")
    print("=" * 70)
    for clip in clips:
        print(f"\nClip {clip['clip_number']}:")
        print(f"  Path: {clip['path']}")
        print(f"  Duration: {clip['duration']:.2f}s")
        print(f"  Description: {clip['description']}")
        print(f"  Strategy: {clip.get('strategy', 'N/A')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
