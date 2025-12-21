"""
Video Processor
===============
This module handles all video processing operations for the Affilify TikTok system.

Key functions:
1. Convert videos to 9:16 aspect ratio (TikTok vertical format)
2. Split long videos into multiple clips
3. Add text overlays highlighting Affilify features
4. Generate unique variations for each account
5. Optimize for TikTok's algorithm (quality, duration, format)

This ensures that each of the 60 accounts posts unique, optimized content.
"""

import os
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips
)
from moviepy.video.fx import resize, crop

logger = logging.getLogger(__name__)


class VideoProcessingError(Exception):
    """Custom exception for video processing errors."""
    pass


class VideoProcessor:
    """
    Handles all video processing operations.
    
    This class provides methods to:
    - Convert videos to TikTok format (9:16)
    - Split videos into clips
    - Add text overlays
    - Generate unique variations
    - Optimize for TikTok
    """
    
    # TikTok optimal specifications
    TIKTOK_WIDTH = 1080
    TIKTOK_HEIGHT = 1920
    TIKTOK_ASPECT_RATIO = 9 / 16
    TIKTOK_MAX_DURATION = 60  # seconds
    TIKTOK_MIN_DURATION = 3   # seconds
    TIKTOK_FPS = 30
    
    def __init__(self, output_dir: str):
        """
        Initialize the video processor.
        
        Args:
            output_dir: Directory where processed videos will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"VideoProcessor initialized with output dir: {self.output_dir}")
    
    def convert_to_tiktok_format(self, input_path: str, 
                                 output_path: Optional[str] = None,
                                 crop_method: str = "center") -> str:
        """
        Convert a video to TikTok's 9:16 vertical format.
        
        Args:
            input_path: Path to the input video file
            output_path: Optional output path (auto-generated if not provided)
            crop_method: How to crop ("center", "top", "bottom")
        
        Returns:
            Path to the converted video
        
        Raises:
            VideoProcessingError: If conversion fails
        """
        logger.info(f"Converting video to TikTok format: {input_path}")
        
        try:
            # Load the video
            clip = VideoFileClip(input_path)
            
            # Get original dimensions
            orig_width, orig_height = clip.size
            orig_aspect = orig_width / orig_height
            
            logger.debug(f"Original size: {orig_width}x{orig_height} (aspect: {orig_aspect:.2f})")
            
            # Determine if we need to crop or letterbox
            if orig_aspect > self.TIKTOK_ASPECT_RATIO:
                # Video is too wide - crop the sides
                new_width = int(orig_height * self.TIKTOK_ASPECT_RATIO)
                
                if crop_method == "center":
                    x_center = orig_width / 2
                    x1 = x_center - new_width / 2
                elif crop_method == "left":
                    x1 = 0
                else:  # right
                    x1 = orig_width - new_width
                
                clip = crop.crop(clip, x1=int(x1), width=new_width)
            
            elif orig_aspect < self.TIKTOK_ASPECT_RATIO:
                # Video is too tall - crop top/bottom
                new_height = int(orig_width / self.TIKTOK_ASPECT_RATIO)
                
                if crop_method == "center":
                    y_center = orig_height / 2
                    y1 = y_center - new_height / 2
                elif crop_method == "top":
                    y1 = 0
                else:  # bottom
                    y1 = orig_height - new_height
                
                clip = crop.crop(clip, y1=int(y1), height=new_height)
            
            # Resize to TikTok dimensions
            clip = resize.resize(clip, (self.TIKTOK_WIDTH, self.TIKTOK_HEIGHT))
            
            # Set FPS
            clip = clip.set_fps(self.TIKTOK_FPS)
            
            # Generate output path if not provided
            if output_path is None:
                input_name = Path(input_path).stem
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.output_dir / f"{input_name}_tiktok_{timestamp}.mp4"
            
            # Write the output
            clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=self.TIKTOK_FPS,
                preset='medium',
                bitrate='8000k'
            )
            
            # Clean up
            clip.close()
            
            logger.info(f"Successfully converted video: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to convert video: {e}")
            raise VideoProcessingError(f"Video conversion failed: {e}")
    
    def split_video(self, input_path: str, 
                   clip_duration: int = 30,
                   max_clips: Optional[int] = None) -> List[str]:
        """
        Split a video into multiple clips.
        
        Args:
            input_path: Path to the input video
            clip_duration: Duration of each clip in seconds
            max_clips: Maximum number of clips to create (None for all)
        
        Returns:
            List of paths to the created clips
        
        Raises:
            VideoProcessingError: If splitting fails
        """
        logger.info(f"Splitting video: {input_path} (clip duration: {clip_duration}s)")
        
        try:
            clip = VideoFileClip(input_path)
            total_duration = clip.duration
            
            # Calculate number of clips
            num_clips = int(total_duration / clip_duration)
            
            if max_clips:
                num_clips = min(num_clips, max_clips)
            
            logger.info(f"Creating {num_clips} clips from {total_duration:.1f}s video")
            
            output_paths = []
            input_name = Path(input_path).stem
            
            for i in range(num_clips):
                start_time = i * clip_duration
                end_time = min((i + 1) * clip_duration, total_duration)
                
                # Extract the subclip
                subclip = clip.subclip(start_time, end_time)
                
                # Generate output path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.output_dir / f"{input_name}_clip_{i+1:03d}_{timestamp}.mp4"
                
                # Write the clip
                subclip.write_videofile(
                    str(output_path),
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=f'temp-audio-{i}.m4a',
                    remove_temp=True,
                    fps=self.TIKTOK_FPS,
                    preset='medium',
                    bitrate='8000k'
                )
                
                output_paths.append(str(output_path))
                logger.info(f"Created clip {i+1}/{num_clips}: {output_path}")
            
            # Clean up
            clip.close()
            
            return output_paths
        
        except Exception as e:
            logger.error(f"Failed to split video: {e}")
            raise VideoProcessingError(f"Video splitting failed: {e}")
    
    def add_text_overlay(self, input_path: str,
                        text: str,
                        position: Tuple[str, str] = ("center", "bottom"),
                        font_size: int = 70,
                        font_color: str = "white",
                        bg_color: str = "black",
                        bg_opacity: float = 0.6,
                        duration: Optional[float] = None,
                        output_path: Optional[str] = None) -> str:
        """
        Add a text overlay to a video.
        
        Args:
            input_path: Path to the input video
            text: Text to overlay
            position: Position tuple (horizontal, vertical)
            font_size: Font size in pixels
            font_color: Font color
            bg_color: Background color
            bg_opacity: Background opacity (0-1)
            duration: Duration of text (None for entire video)
            output_path: Optional output path
        
        Returns:
            Path to the video with text overlay
        
        Raises:
            VideoProcessingError: If overlay fails
        """
        logger.info(f"Adding text overlay: '{text}' to {input_path}")
        
        try:
            # Load the video
            video = VideoFileClip(input_path)
            
            # Create text clip
            txt_clip = TextClip(
                text,
                fontsize=font_size,
                color=font_color,
                font='Arial-Bold',
                method='caption',
                size=(self.TIKTOK_WIDTH - 100, None),  # Leave margins
                align='center'
            )
            
            # Set duration
            if duration is None:
                duration = video.duration
            
            txt_clip = txt_clip.set_duration(duration)
            
            # Position the text
            txt_clip = txt_clip.set_position(position)
            
            # Create background for text (for better readability)
            if bg_opacity > 0:
                # Add a semi-transparent background
                txt_clip = txt_clip.on_color(
                    size=(txt_clip.w + 40, txt_clip.h + 20),
                    color=bg_color,
                    pos=('center', 'center'),
                    col_opacity=bg_opacity
                )
            
            # Composite the text over the video
            final_video = CompositeVideoClip([video, txt_clip])
            
            # Generate output path if not provided
            if output_path is None:
                input_name = Path(input_path).stem
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.output_dir / f"{input_name}_overlay_{timestamp}.mp4"
            
            # Write the output
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio-overlay.m4a',
                remove_temp=True,
                fps=self.TIKTOK_FPS,
                preset='medium',
                bitrate='8000k'
            )
            
            # Clean up
            video.close()
            txt_clip.close()
            final_video.close()
            
            logger.info(f"Successfully added text overlay: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to add text overlay: {e}")
            raise VideoProcessingError(f"Text overlay failed: {e}")
    
    def generate_unique_variation(self, input_path: str,
                                  variation_index: int,
                                  total_variations: int) -> str:
        """
        Generate a unique variation of a video.
        
        This creates subtle variations to ensure each account posts
        a unique file (different hash) to avoid TikTok duplicate detection.
        
        Variations include:
        - Slight speed adjustments (0.98x - 1.02x)
        - Different start/end trim (0.1-0.3 seconds)
        - Unique metadata
        
        Args:
            input_path: Path to the input video
            variation_index: Index of this variation (0-based)
            total_variations: Total number of variations to create
        
        Returns:
            Path to the unique variation
        
        Raises:
            VideoProcessingError: If variation generation fails
        """
        logger.info(f"Generating variation {variation_index + 1}/{total_variations} for {input_path}")
        
        try:
            clip = VideoFileClip(input_path)
            
            # Calculate unique speed factor (0.98x to 1.02x)
            speed_range = 0.04  # 4% range
            speed_factor = 0.98 + (variation_index / max(total_variations - 1, 1)) * speed_range
            
            # Apply speed change
            clip = clip.fx(lambda c: c.speedx(speed_factor))
            
            # Calculate unique trim (0.05 to 0.15 seconds from start)
            trim_range = 0.10
            start_trim = 0.05 + (variation_index / max(total_variations - 1, 1)) * trim_range
            
            # Trim if video is long enough
            if clip.duration > 5:
                clip = clip.subclip(start_trim, clip.duration - 0.05)
            
            # Generate output path
            input_name = Path(input_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{input_name}_var_{variation_index+1:03d}_{timestamp}.mp4"
            
            # Write with unique metadata
            clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=f'temp-audio-var-{variation_index}.m4a',
                remove_temp=True,
                fps=self.TIKTOK_FPS,
                preset='medium',
                bitrate='8000k'
            )
            
            # Clean up
            clip.close()
            
            # Calculate file hash for verification
            file_hash = self.calculate_file_hash(output_path)
            logger.info(f"Created variation {variation_index + 1} (hash: {file_hash[:8]}...): {output_path}")
            
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to generate variation: {e}")
            raise VideoProcessingError(f"Variation generation failed: {e}")
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
        """
        Calculate the hash of a file.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm ("md5", "sha256", etc.)
        
        Returns:
            Hexadecimal hash string
        """
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def get_video_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a video file.
        
        Args:
            file_path: Path to the video file
        
        Returns:
            Dictionary containing video information
        """
        try:
            clip = VideoFileClip(file_path)
            
            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,
                'width': clip.w,
                'height': clip.h,
                'aspect_ratio': clip.w / clip.h,
                'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024),
                'file_hash': self.calculate_file_hash(file_path)
            }
            
            clip.close()
            
            return info
        
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return {}


if __name__ == "__main__":
    # Test the video processor
    logging.basicConfig(level=logging.INFO)
    
    print("VideoProcessor module loaded successfully!")
    print("=" * 80)
    print("This module provides video processing capabilities for the Affilify system.")
    print("=" * 80)
