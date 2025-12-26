#!/usr/bin/env python3
"""
Background Music Adder
======================
Adds royalty-free background music to videos.

Note: This adds generic background music. TikTok's trending music
cannot be added programmatically due to licensing restrictions.

For trending music, you must:
1. Post video without music via automation
2. Manually add trending sound in TikTok app
3. Or use TikTok's web interface after upload

Usage:
    python3 add_background_music.py --input video.mp4 --music background.mp3 --output output.mp4
"""

import argparse
import logging
from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_background_music(video_path: str, music_path: str, output_path: str, 
                        volume: float = 0.3, loop: bool = True):
    """
    Add background music to a video.
    
    Args:
        video_path: Path to input video
        music_path: Path to music file (MP3, WAV, etc.)
        output_path: Path for output video
        volume: Music volume (0.0 to 1.0)
        loop: Whether to loop music if shorter than video
    """
    logger.info(f"Adding background music to {video_path}")
    
    try:
        # Load video
        video = VideoFileClip(video_path)
        
        # Load music
        music = AudioFileClip(music_path)
        
        # Adjust music volume
        music = music.volumex(volume)
        
        # Loop music if needed
        if loop and music.duration < video.duration:
            # Calculate how many times to loop
            loops_needed = int(video.duration / music.duration) + 1
            music = music.loop(loops_needed)
        
        # Trim music to video length
        music = music.subclip(0, video.duration)
        
        # Combine original audio (if exists) with background music
        if video.audio:
            # Mix original audio with background music
            final_audio = CompositeAudioClip([video.audio, music])
        else:
            # Just use background music
            final_audio = music
        
        # Set the audio
        final_video = video.set_audio(final_audio)
        
        # Write output
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio-music.m4a',
            remove_temp=True,
            fps=30,
            preset='medium',
            bitrate='8000k'
        )
        
        # Cleanup
        video.close()
        music.close()
        final_video.close()
        
        logger.info(f"✅ Successfully added music: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"❌ Failed to add music: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Add background music to videos"
    )
    parser.add_argument('--input', required=True, help='Input video file')
    parser.add_argument('--music', required=True, help='Music file (MP3, WAV, etc.)')
    parser.add_argument('--output', required=True, help='Output video file')
    parser.add_argument('--volume', type=float, default=0.3, 
                       help='Music volume (0.0-1.0, default: 0.3)')
    parser.add_argument('--no-loop', action='store_true',
                       help='Do not loop music if shorter than video')
    
    args = parser.parse_args()
    
    # Validate files exist
    if not Path(args.input).exists():
        logger.error(f"Input video not found: {args.input}")
        return 1
    
    if not Path(args.music).exists():
        logger.error(f"Music file not found: {args.music}")
        return 1
    
    # Add music
    add_background_music(
        args.input,
        args.music,
        args.output,
        volume=args.volume,
        loop=not args.no_loop
    )
    
    return 0


if __name__ == '__main__':
    exit(main())
