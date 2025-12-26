#!/usr/bin/env python3
"""
Viral Video Editor
==================
Applies viral TikTok editing techniques to maximize engagement.

Based on proven viral strategies:
- Compelling hooks in first 3 seconds
- Rapid cuts and transitions
- Zoom effects on key elements
- Animated text overlays
- Split-screen comparisons
- Celebration animations
- Professional pacing

This module transforms basic screen recordings into viral-ready content.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from moviepy import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    ImageClip,
    ColorClip
)
from moviepy.video import fx

logger = logging.getLogger(__name__)


class ViralEditor:
    """
    Applies viral editing techniques to videos.
    
    Implements proven TikTok strategies:
    - Hook optimization
    - Dynamic pacing
    - Visual emphasis
    - Engagement triggers
    """
    
    # Viral editing parameters
    HOOK_DURATION = 3  # First 3 seconds are critical
    RAPID_CUT_INTERVAL = 2  # Cut every 2 seconds for engagement
    ZOOM_EMPHASIS_SCALE = 1.2  # 20% zoom for emphasis
    TEXT_ANIMATION_DURATION = 0.5  # Text fade in/out
    
    # Text overlay styles
    HOOK_TEXT_STYLE = {
        "fontsize": 80,
        "color": "white",
        "font": "Arial-Bold",
        "stroke_color": "black",
        "stroke_width": 3
    }
    
    CAPTION_TEXT_STYLE = {
        "fontsize": 60,
        "color": "white",
        "font": "Arial-Bold",
        "stroke_color": "black",
        "stroke_width": 2
    }
    
    CTA_TEXT_STYLE = {
        "fontsize": 70,
        "color": "yellow",
        "font": "Arial-Bold",
        "stroke_color": "black",
        "stroke_width": 3
    }
    
    def __init__(self, output_dir: str):
        """
        Initialize the viral editor.
        
        Args:
            output_dir: Directory for output videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ViralEditor initialized with output dir: {self.output_dir}")
    
    def add_compelling_hook(self,
                          video_path: str,
                          hook_text: str,
                          hook_type: str = "problem_solution") -> str:
        """
        Add a compelling hook in the first 3 seconds.
        
        Hook types:
        - "problem_solution": "Tired of ugly affiliate links? Watch this!"
        - "challenge": "What if you could build this in 30 seconds?"
        - "reveal": "The secret weapon for affiliate success"
        - "question": "Want to know how I made $10k?"
        
        Args:
            video_path: Path to input video
            hook_text: Hook text to display
            hook_type: Type of hook
        
        Returns:
            Path to video with hook
        """
        logger.info(f"Adding {hook_type} hook: {hook_text}")
        
        try:
            video = VideoFileClip(video_path)
            
            # Create hook text clip
            hook_clip = TextClip(
                hook_text,
                **self.HOOK_TEXT_STYLE,
                method='caption',
                size=(1000, None),
                align='center'
            )
            
            # Position at top of screen
            hook_clip = hook_clip.set_position(('center', 100))
            hook_clip = hook_clip.set_duration(self.HOOK_DURATION)
            
            # Add fade in/out animation
            hook_clip = hook_clip.crossfadein(0.3).crossfadeout(0.3)
            
            # Composite over video
            final_video = CompositeVideoClip([video, hook_clip])
            
            # Generate output path
            output_path = self.output_dir / f"{Path(video_path).stem}_hook.mp4"
            
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium'
            )
            
            video.close()
            hook_clip.close()
            final_video.close()
            
            logger.info(f"Hook added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to add hook: {e}")
            return video_path
    
    def add_rapid_cuts(self,
                      video_path: str,
                      cut_interval: float = 2.0,
                      zoom_on_cuts: bool = True) -> str:
        """
        Add rapid cuts to maintain engagement.
        
        Cuts video into segments and adds subtle zoom/position changes
        to create dynamic pacing.
        
        Args:
            video_path: Path to input video
            cut_interval: Seconds between cuts
            zoom_on_cuts: Whether to add zoom effects
        
        Returns:
            Path to video with rapid cuts
        """
        logger.info(f"Adding rapid cuts every {cut_interval}s")
        
        try:
            video = VideoFileClip(video_path)
            duration = video.duration
            
            # Calculate number of cuts
            num_segments = int(duration / cut_interval)
            
            segments = []
            for i in range(num_segments):
                start = i * cut_interval
                end = min((i + 1) * cut_interval, duration)
                
                segment = video.subclip(start, end)
                
                # Add subtle zoom on alternating segments
                if zoom_on_cuts and i % 2 == 1:
                    segment = fx.resize(segment, 1.1)  # 10% zoom
                
                segments.append(segment)
            
            # Concatenate segments
            from moviepy import concatenate_videoclips
            final_video = concatenate_videoclips(segments, method="compose")
            
            output_path = self.output_dir / f"{Path(video_path).stem}_cuts.mp4"
            
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium'
            )
            
            video.close()
            final_video.close()
            
            logger.info(f"Rapid cuts added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to add rapid cuts: {e}")
            return video_path
    
    def add_zoom_emphasis(self,
                         video_path: str,
                         zoom_times: List[float],
                         zoom_duration: float = 1.0) -> str:
        """
        Add zoom effects at key moments for emphasis.
        
        Args:
            video_path: Path to input video
            zoom_times: List of timestamps to add zoom
            zoom_duration: Duration of each zoom
        
        Returns:
            Path to video with zoom effects
        """
        logger.info(f"Adding {len(zoom_times)} zoom effects")
        
        try:
            video = VideoFileClip(video_path)
            
            # For each zoom time, create a zoomed segment
            clips = []
            last_time = 0
            
            for zoom_time in sorted(zoom_times):
                # Add normal segment before zoom
                if zoom_time > last_time:
                    clips.append(video.subclip(last_time, zoom_time))
                
                # Add zoomed segment
                zoom_end = min(zoom_time + zoom_duration, video.duration)
                zoomed = video.subclip(zoom_time, zoom_end)
                zoomed = fx.resize(zoomed, self.ZOOM_EMPHASIS_SCALE)
                clips.append(zoomed)
                
                last_time = zoom_end
            
            # Add remaining video
            if last_time < video.duration:
                clips.append(video.subclip(last_time, video.duration))
            
            # Concatenate
            from moviepy import concatenate_videoclips
            final_video = concatenate_videoclips(clips, method="compose")
            
            output_path = self.output_dir / f"{Path(video_path).stem}_zoom.mp4"
            
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium'
            )
            
            video.close()
            final_video.close()
            
            logger.info(f"Zoom effects added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to add zoom effects: {e}")
            return video_path
    
    def add_animated_text_overlays(self,
                                  video_path: str,
                                  text_overlays: List[Dict[str, Any]]) -> str:
        """
        Add animated text overlays at specific times.
        
        Args:
            video_path: Path to input video
            text_overlays: List of overlay configs with:
                - text: Text to display
                - start_time: When to show
                - duration: How long to show
                - position: Where to show ('top', 'center', 'bottom')
                - style: 'hook', 'caption', or 'cta'
        
        Returns:
            Path to video with text overlays
        """
        logger.info(f"Adding {len(text_overlays)} text overlays")
        
        try:
            video = VideoFileClip(video_path)
            
            text_clips = []
            for overlay in text_overlays:
                # Select style
                if overlay.get('style') == 'hook':
                    style = self.HOOK_TEXT_STYLE
                elif overlay.get('style') == 'cta':
                    style = self.CTA_TEXT_STYLE
                else:
                    style = self.CAPTION_TEXT_STYLE
                
                # Create text clip
                txt = TextClip(
                    overlay['text'],
                    **style,
                    method='caption',
                    size=(1000, None),
                    align='center'
                )
                
                # Position
                position_map = {
                    'top': ('center', 100),
                    'center': ('center', 'center'),
                    'bottom': ('center', 1700)
                }
                txt = txt.set_position(position_map.get(overlay.get('position', 'center')))
                
                # Timing
                txt = txt.set_start(overlay['start_time'])
                txt = txt.set_duration(overlay['duration'])
                
                # Animation
                txt = txt.crossfadein(self.TEXT_ANIMATION_DURATION)
                txt = txt.crossfadeout(self.TEXT_ANIMATION_DURATION)
                
                text_clips.append(txt)
            
            # Composite all text over video
            final_video = CompositeVideoClip([video] + text_clips)
            
            output_path = self.output_dir / f"{Path(video_path).stem}_text.mp4"
            
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium'
            )
            
            video.close()
            for clip in text_clips:
                clip.close()
            final_video.close()
            
            logger.info(f"Text overlays added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to add text overlays: {e}")
            return video_path
    
    def create_split_screen_comparison(self,
                                      before_video: str,
                                      after_video: str,
                                      label_before: str = "BEFORE",
                                      label_after: str = "AFTER") -> str:
        """
        Create split-screen before/after comparison.
        
        Perfect for showing:
        - Original product page vs AFFILIFY site
        - Ugly link vs beautiful website
        - Manual work vs AI automation
        
        Args:
            before_video: Path to "before" video
            after_video: Path to "after" video
            label_before: Label for before side
            label_after: Label for after side
        
        Returns:
            Path to split-screen video
        """
        logger.info("Creating split-screen comparison")
        
        try:
            before = VideoFileClip(before_video)
            after = VideoFileClip(after_video)
            
            # Resize both to half width
            before_half = fx.resize(before, width=540)
            after_half = fx.resize(after, width=540)
            
            # Position side by side
            before_half = before_half.set_position((0, 0))
            after_half = after_half.set_position((540, 0))
            
            # Create labels
            before_label = TextClip(
                label_before,
                fontsize=50,
                color='red',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2
            )
            before_label = before_label.set_position((100, 50))
            before_label = before_label.set_duration(min(before.duration, after.duration))
            
            after_label = TextClip(
                label_after,
                fontsize=50,
                color='green',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2
            )
            after_label = after_label.set_position((640, 50))
            after_label = after_label.set_duration(min(before.duration, after.duration))
            
            # Composite
            final_video = CompositeVideoClip([
                before_half,
                after_half,
                before_label,
                after_label
            ])
            
            output_path = self.output_dir / f"comparison_{Path(before_video).stem}.mp4"
            
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium'
            )
            
            before.close()
            after.close()
            final_video.close()
            
            logger.info(f"Split-screen created: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to create split-screen: {e}")
            return before_video
    
    def add_celebration_animation(self,
                                 video_path: str,
                                 trigger_time: float,
                                 animation_type: str = "checkmark") -> str:
        """
        Add celebration animation (confetti, checkmark, etc.) at key moment.
        
        Args:
            video_path: Path to input video
            trigger_time: When to show animation
            animation_type: Type of animation ('checkmark', 'confetti', 'star')
        
        Returns:
            Path to video with celebration
        """
        logger.info(f"Adding {animation_type} celebration at {trigger_time}s")
        
        try:
            video = VideoFileClip(video_path)
            
            # Create celebration text (simplified - in production use actual animations)
            if animation_type == "checkmark":
                celebration_text = "✓"
                color = "green"
            elif animation_type == "star":
                celebration_text = "⭐"
                color = "yellow"
            else:  # confetti
                celebration_text = "🎉"
                color = "white"
            
            celebration = TextClip(
                celebration_text,
                fontsize=150,
                color=color,
                font='Arial-Bold'
            )
            
            celebration = celebration.set_position(('center', 'center'))
            celebration = celebration.set_start(trigger_time)
            celebration = celebration.set_duration(1.0)
            celebration = celebration.crossfadein(0.2).crossfadeout(0.3)
            
            final_video = CompositeVideoClip([video, celebration])
            
            output_path = self.output_dir / f"{Path(video_path).stem}_celebration.mp4"
            
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium'
            )
            
            video.close()
            celebration.close()
            final_video.close()
            
            logger.info(f"Celebration added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to add celebration: {e}")
            return video_path
    
    def apply_full_viral_treatment(self,
                                  video_path: str,
                                  config: Dict[str, Any]) -> str:
        """
        Apply complete viral editing treatment to a video.
        
        Args:
            video_path: Path to input video
            config: Configuration with:
                - hook_text: Hook text for first 3 seconds
                - text_overlays: List of text overlays
                - zoom_times: Times to add zoom emphasis
                - celebration_time: When to show celebration
                - add_rapid_cuts: Whether to add rapid cuts
        
        Returns:
            Path to fully edited video
        """
        logger.info(f"Applying full viral treatment to {video_path}")
        
        current_video = video_path
        
        try:
            # 1. Add hook
            if config.get('hook_text'):
                current_video = self.add_compelling_hook(
                    current_video,
                    config['hook_text'],
                    config.get('hook_type', 'problem_solution')
                )
            
            # 2. Add rapid cuts
            if config.get('add_rapid_cuts', True):
                current_video = self.add_rapid_cuts(current_video)
            
            # 3. Add zoom emphasis
            if config.get('zoom_times'):
                current_video = self.add_zoom_emphasis(
                    current_video,
                    config['zoom_times']
                )
            
            # 4. Add text overlays
            if config.get('text_overlays'):
                current_video = self.add_animated_text_overlays(
                    current_video,
                    config['text_overlays']
                )
            
            # 5. Add celebration
            if config.get('celebration_time') is not None:
                current_video = self.add_celebration_animation(
                    current_video,
                    config['celebration_time']
                )
            
            logger.info(f"✅ Viral treatment complete: {current_video}")
            return current_video
        
        except Exception as e:
            logger.error(f"Failed to apply viral treatment: {e}")
            return video_path


if __name__ == "__main__":
    # Test the viral editor
    logging.basicConfig(level=logging.INFO)
    
    print("ViralEditor module loaded successfully!")
    print("=" * 80)
    print("This module provides viral editing techniques:")
    print("- Compelling hooks in first 3 seconds")
    print("- Rapid cuts for engagement")
    print("- Zoom emphasis on key moments")
    print("- Animated text overlays")
    print("- Split-screen comparisons")
    print("- Celebration animations")
    print("=" * 80)
