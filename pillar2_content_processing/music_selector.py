#!/usr/bin/env python3
"""
Trending Royalty-Free Music Selector
=====================================
Uses Gemini AI to find royalty-free music that matches trending TikTok sounds.

This module:
1. Analyzes current trending TikTok music styles
2. Finds royalty-free alternatives with similar vibes
3. Recommends music from free libraries (Pixabay, Epidemic Sound, etc.)
4. Matches music to video content and mood

Since TikTok's actual trending music is copyrighted, this finds the closest
royalty-free alternatives that capture the same energy and style.
"""

import os
import sys
import logging
import json
import random
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class MusicSelector:
    """
    Selects trending-style royalty-free music for videos.
    
    Uses Gemini AI to analyze trending music styles and recommend
    royalty-free alternatives that capture the same vibe.
    """
    
    # Royalty-free music sources
    MUSIC_SOURCES = {
        "pixabay": "https://pixabay.com/music/",
        "youtube_audio_library": "https://www.youtube.com/audiolibrary",
        "free_music_archive": "https://freemusicarchive.org/",
        "incompetech": "https://incompetech.com/music/",
        "bensound": "https://www.bensound.com/",
        "audionautix": "https://audionautix.com/"
    }
    
    # Music categories for affiliate marketing content
    MUSIC_CATEGORIES = {
        "upbeat_energetic": "High energy, motivational, perfect for product reveals",
        "tech_modern": "Electronic, futuristic, great for AI/tech content",
        "inspiring_success": "Uplifting, aspirational, ideal for success stories",
        "trendy_viral": "Current viral sound style, catchy and memorable",
        "chill_professional": "Smooth, professional, good for tutorials",
        "hype_exciting": "Exciting, builds anticipation, perfect for launches"
    }
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the music selector.
        
        Args:
            gemini_api_key: Gemini API key (reads from env if not provided)
        """
        self.api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        
        # Initialize Gemini client
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info("Gemini API client initialized for music selection")
            except ImportError:
                logger.error("OpenAI package not installed")
        
        logger.info("MusicSelector initialized")
    
    def get_trending_music_styles(self) -> List[Dict[str, str]]:
        """
        Analyze current trending TikTok music styles using Gemini AI.
        
        Returns:
            List of trending music styles with descriptions
        """
        if not self.client:
            # Fallback to predefined trending styles
            return self._get_default_trending_styles()
        
        try:
            prompt = """
            Analyze the current trending music styles on TikTok (December 2025).
            
            Focus on music that works well for:
            - Affiliate marketing content
            - Product demonstrations
            - AI/tech showcases
            - Success stories
            - Tutorial videos
            
            For each trending style, provide:
            1. Style name (e.g., "Upbeat Electronic", "Viral Pop Hook")
            2. BPM range
            3. Key characteristics (instruments, mood, energy level)
            4. Why it's trending
            5. Best use cases for affiliate content
            
            Return as JSON array with 10 trending styles.
            """
            
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            trending_styles = json.loads(content)
            logger.info(f"Retrieved {len(trending_styles)} trending music styles from Gemini")
            
            return trending_styles
        
        except Exception as e:
            logger.error(f"Failed to get trending styles from Gemini: {e}")
            return self._get_default_trending_styles()
    
    def find_royalty_free_match(self, 
                               video_content: str,
                               trending_style: Optional[str] = None) -> Dict[str, Any]:
        """
        Find royalty-free music that matches trending styles for given content.
        
        Args:
            video_content: Description of the video content
            trending_style: Optional specific trending style to match
        
        Returns:
            Dictionary with music recommendations
        """
        if not self.client:
            return self._get_default_music_recommendation(video_content)
        
        try:
            prompt = f"""
            Find royalty-free music that matches current TikTok trending sounds.
            
            Video content: {video_content}
            {f"Target trending style: {trending_style}" if trending_style else ""}
            
            Recommend music from these royalty-free sources:
            - Pixabay Music
            - YouTube Audio Library
            - Free Music Archive
            - Incompetech
            - Bensound
            - Audionautix
            
            Provide:
            1. Music title and artist
            2. Source (which library)
            3. Style/genre
            4. BPM
            5. Mood/energy level
            6. Why it matches trending TikTok sounds
            7. Search keywords to find it
            8. Direct link if available
            
            Focus on music that:
            - Sounds similar to current TikTok viral sounds
            - Is upbeat and engaging
            - Works for 15-60 second videos
            - Enhances affiliate marketing content
            - Is completely royalty-free
            
            Return top 5 recommendations as JSON array.
            """
            
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            recommendations = json.loads(content)
            logger.info(f"Generated {len(recommendations)} music recommendations")
            
            return {
                "recommendations": recommendations,
                "video_content": video_content,
                "trending_style": trending_style
            }
        
        except Exception as e:
            logger.error(f"Failed to generate music recommendations: {e}")
            return self._get_default_music_recommendation(video_content)
    
    def select_music_for_batch(self, 
                              video_descriptions: List[str],
                              ensure_variety: bool = True) -> List[Dict[str, Any]]:
        """
        Select music for a batch of videos, ensuring variety.
        
        Args:
            video_descriptions: List of video content descriptions
            ensure_variety: Whether to ensure different music for each video
        
        Returns:
            List of music selections, one per video
        """
        logger.info(f"Selecting music for {len(video_descriptions)} videos")
        
        # Get trending styles first
        trending_styles = self.get_trending_music_styles()
        
        selections = []
        used_tracks = set()
        
        for i, description in enumerate(video_descriptions):
            # Rotate through trending styles for variety
            style = trending_styles[i % len(trending_styles)] if trending_styles else None
            style_name = style.get('name') if isinstance(style, dict) else None
            
            # Get recommendation
            recommendation = self.find_royalty_free_match(description, style_name)
            
            if ensure_variety and recommendation.get('recommendations'):
                # Pick a track we haven't used yet
                for track in recommendation['recommendations']:
                    track_id = f"{track.get('title')}_{track.get('artist')}"
                    if track_id not in used_tracks:
                        used_tracks.add(track_id)
                        selections.append({
                            'video_index': i,
                            'video_description': description,
                            'selected_track': track,
                            'trending_style': style
                        })
                        break
                else:
                    # All tracks used, just pick the first one
                    selections.append({
                        'video_index': i,
                        'video_description': description,
                        'selected_track': recommendation['recommendations'][0],
                        'trending_style': style
                    })
            else:
                # No variety requirement or no recommendations
                selections.append({
                    'video_index': i,
                    'video_description': description,
                    'recommendation': recommendation,
                    'trending_style': style
                })
        
        logger.info(f"Selected {len(selections)} music tracks")
        return selections
    
    def generate_music_report(self, 
                            selections: List[Dict[str, Any]],
                            output_path: str) -> str:
        """
        Generate a report of music selections for easy reference.
        
        Args:
            selections: List of music selections
            output_path: Path to save the report
        
        Returns:
            Path to the generated report
        """
        report_lines = [
            "=" * 80,
            "AFFILIFY TIKTOK - MUSIC SELECTION REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total videos: {len(selections)}",
            "",
            "INSTRUCTIONS:",
            "1. Download music from the provided sources",
            "2. Use tools/add_background_music.py to add music to videos",
            "3. All music listed is royalty-free and TikTok-safe",
            "",
            "=" * 80,
            ""
        ]
        
        for i, selection in enumerate(selections, 1):
            track = selection.get('selected_track', {})
            
            report_lines.extend([
                f"VIDEO {i}",
                "-" * 80,
                f"Content: {selection.get('video_description', 'N/A')}",
                f"",
                f"RECOMMENDED MUSIC:",
                f"  Title: {track.get('title', 'N/A')}",
                f"  Artist: {track.get('artist', 'N/A')}",
                f"  Source: {track.get('source', 'N/A')}",
                f"  Style: {track.get('style', 'N/A')}",
                f"  BPM: {track.get('bpm', 'N/A')}",
                f"  Mood: {track.get('mood', 'N/A')}",
                f"  Why it works: {track.get('why_matches', 'N/A')}",
                f"  Search keywords: {track.get('search_keywords', 'N/A')}",
                f"  Link: {track.get('link', 'Search on source website')}",
                "",
                f"TRENDING STYLE MATCH:",
                f"  {selection.get('trending_style', {}).get('name', 'N/A')}",
                "",
                ""
            ])
        
        # Write report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Music report generated: {output_path}")
        return output_path
    
    def _get_default_trending_styles(self) -> List[Dict[str, str]]:
        """Fallback trending styles when Gemini is unavailable."""
        return [
            {
                "name": "Upbeat Electronic Pop",
                "bpm": "120-130",
                "characteristics": "Synth-heavy, energetic, catchy hooks",
                "why_trending": "Perfect for product reveals and success stories",
                "use_case": "AI demonstrations, feature showcases"
            },
            {
                "name": "Viral Hip-Hop Beat",
                "bpm": "140-150",
                "characteristics": "Strong bass, rhythmic, modern",
                "why_trending": "High energy, keeps viewers engaged",
                "use_case": "Quick tutorials, before/after comparisons"
            },
            {
                "name": "Motivational Indie",
                "bpm": "110-120",
                "characteristics": "Uplifting, inspiring, acoustic elements",
                "why_trending": "Emotional connection, aspirational",
                "use_case": "Success stories, testimonials"
            },
            {
                "name": "Tech House",
                "bpm": "125-130",
                "characteristics": "Electronic, futuristic, clean",
                "why_trending": "Modern, professional vibe",
                "use_case": "Tech demos, AI features"
            },
            {
                "name": "Chill Lo-Fi",
                "bpm": "80-95",
                "characteristics": "Relaxed, smooth, professional",
                "why_trending": "Easy to listen to, non-intrusive",
                "use_case": "Longer tutorials, explanations"
            }
        ]
    
    def _get_default_music_recommendation(self, video_content: str) -> Dict[str, Any]:
        """Fallback music recommendation when Gemini is unavailable."""
        
        # Simple keyword-based matching
        content_lower = video_content.lower()
        
        if any(word in content_lower for word in ['ai', 'tech', 'future', 'modern']):
            category = "tech_modern"
        elif any(word in content_lower for word in ['success', 'money', 'earn', 'profit']):
            category = "inspiring_success"
        elif any(word in content_lower for word in ['fast', 'quick', 'instant', 'easy']):
            category = "upbeat_energetic"
        elif any(word in content_lower for word in ['tutorial', 'how to', 'guide']):
            category = "chill_professional"
        else:
            category = "trendy_viral"
        
        recommendations = [
            {
                "title": f"Upbeat {category.replace('_', ' ').title()} Track",
                "artist": "Various Artists",
                "source": "Pixabay Music",
                "style": category.replace('_', ' ').title(),
                "bpm": "120-130",
                "mood": "Energetic and engaging",
                "why_matches": f"Perfect for {video_content[:50]}...",
                "search_keywords": f"{category} royalty free music",
                "link": f"https://pixabay.com/music/search/{category}/"
            }
        ]
        
        return {
            "recommendations": recommendations,
            "video_content": video_content,
            "trending_style": category
        }


if __name__ == "__main__":
    # Test the music selector
    logging.basicConfig(level=logging.INFO)
    
    selector = MusicSelector()
    
    # Test with sample video descriptions
    test_videos = [
        "AI-powered website builder demonstration showing instant results",
        "Before and after comparison of affiliate links",
        "Success story: How I made $10k with AFFILIFY"
    ]
    
    print("Testing music selector...")
    print("=" * 80)
    
    # Get trending styles
    print("\n1. Getting trending music styles...")
    styles = selector.get_trending_music_styles()
    print(f"Found {len(styles)} trending styles")
    
    # Get recommendations for videos
    print("\n2. Selecting music for videos...")
    selections = selector.select_music_for_batch(test_videos)
    print(f"Selected music for {len(selections)} videos")
    
    # Generate report
    print("\n3. Generating music report...")
    report_path = "/tmp/music_report.txt"
    selector.generate_music_report(selections, report_path)
    print(f"Report saved to: {report_path}")
    
    print("\n✅ Music selector test complete!")
