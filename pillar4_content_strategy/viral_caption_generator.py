#!/usr/bin/env python3
"""
Viral Caption Generator
=======================
Generates TikTok captions optimized for virality using proven hooks and CTAs.

Based on viral content strategies:
- Compelling hooks (Problem/Solution, Challenge, Reveal)
- Strong CTAs that drive action
- Trending hashtags
- Engagement triggers
- AFFILIFY-specific messaging

This module creates captions that stop scrolling and drive conversions.
"""

import os
import sys
import logging
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class ViralCaptionGenerator:
    """
    Generates viral-optimized TikTok captions.
    
    Uses proven hooks, CTAs, and engagement strategies to maximize
    views, engagement, and conversions for AFFILIFY.
    """
    
    # Viral hook templates (from your requirements)
    HOOK_TEMPLATES = {
        "problem_solution": [
            "Tired of ugly affiliate links? Watch this! 🔥",
            "Stop wasting time on ugly links! Here's the solution 💎",
            "Ugly affiliate links killing your sales? Not anymore! ⚡",
            "The #1 problem with affiliate marketing (and how to fix it) 🚀"
        ],
        "challenge": [
            "What if you could build this in 30 seconds? 🤯",
            "Think you can't create a pro website? Watch this! 💪",
            "Challenge: Build a website faster than this video 🎯",
            "Bet you didn't know you could do THIS in 30 seconds! ⚡"
        ],
        "reveal": [
            "The secret weapon for affiliate success 🔓",
            "Revealing my secret to $10k/month affiliate income 💰",
            "This AI just changed the affiliate game forever 🚀",
            "The future of affiliate marketing is here 🌟"
        ],
        "question": [
            "Want to know how I made $10k this month? 💵",
            "What if I told you there's an easier way? 🤔",
            "Ready to 10x your affiliate conversions? 📈",
            "Curious how top affiliates do it? 👀"
        ],
        "transformation": [
            "From ugly link to stunning website in 30 seconds 🎨",
            "Watch me transform this basic link into a sales machine 💎",
            "Zero to pro website in under a minute ⚡",
            "Before: 😔 After: 🤩 (Watch till the end!)"
        ],
        "urgency": [
            "This is changing affiliate marketing RIGHT NOW 🔥",
            "Don't miss this game-changer! ⚠️",
            "Everyone's switching to this (here's why) 📢",
            "The old way is DEAD. Here's the new way 💀➡️✨"
        ]
    }
    
    # Strong CTAs (from your requirements)
    CTA_TEMPLATES = [
        "Visit Affilify.eu to create your AI-powered site! 🚀",
        "Link in bio → Try AFFILIFY now! 💎",
        "Get started at Affilify.eu (it's FREE!) ✨",
        "Click the link in bio to transform your links! 🔗",
        "Try AFFILIFY free → Link in bio! 🎯",
        "Start building at Affilify.eu today! 💪",
        "Your affiliate game is about to change → Affilify.eu 🌟",
        "Ready to dominate? Visit Affilify.eu! 🏆"
    ]
    
    # Engagement triggers
    ENGAGEMENT_QUESTIONS = [
        "What product would you build a site for? 💭",
        "Tag someone who needs this! 👇",
        "Which niche should I try next? Comment below! 💬",
        "Rate this 1-10! 🔥",
        "Who else is tired of ugly links? 🙋",
        "Should I make a tutorial on this? 📚",
        "What feature should I show next? 🤔",
        "Drop a 🔥 if you want to try this!"
    ]
    
    # Trending hashtags (updated for affiliate marketing + AI)
    TRENDING_HASHTAGS = [
        # Core AFFILIFY
        "#affilify", "#affiliatemarketing", "#makemoneyonline",
        
        # Trending money/business
        "#sidehustle", "#entrepreneur", "#passiveincome", "#digitalmarketing",
        "#ecommerce", "#onlinebusiness", "#workfromhome", "#financialfreedom",
        
        # AI/Tech trending
        "#ai", "#aitools", "#artificialintelligence", "#automation", "#tech",
        "#websitebuilder", "#nocode",
        
        # Viral/engagement
        "#viral", "#trending", "#fyp", "#foryou", "#foryoupage",
        
        # Niche specific
        "#affiliatelinks", "#landingpage", "#salesfunnel", "#conversionrate",
        "#digitalproducts", "#affiliateincome"
    ]
    
    # AFFILIFY value propositions
    VALUE_PROPS = [
        "No code, no design skills needed 🎨",
        "AI builds your site in 30 seconds ⚡",
        "Turn ugly links into professional websites 💎",
        "Boost your affiliate conversions instantly 📈",
        "The future of affiliate marketing 🚀",
        "From zero to pro in seconds ⏱️",
        "Stop sharing links, start building experiences 🌟",
        "AI-powered websites that actually convert 💰"
    ]
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the viral caption generator.
        
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
                logger.info("Gemini API client initialized for caption generation")
            except ImportError:
                logger.error("OpenAI package not installed")
        
        logger.info("ViralCaptionGenerator initialized")
    
    def generate_viral_caption(self,
                              video_content: str,
                              hook_type: Optional[str] = None,
                              include_question: bool = True,
                              max_length: int = 2200) -> Dict[str, Any]:
        """
        Generate a complete viral caption with hook, body, CTA, and hashtags.
        
        Args:
            video_content: Description of video content
            hook_type: Type of hook to use (random if None)
            include_question: Whether to include engagement question
            max_length: Maximum caption length (TikTok limit is 2200)
        
        Returns:
            Dictionary with caption components
        """
        # Select hook type
        if not hook_type:
            hook_type = random.choice(list(self.HOOK_TEMPLATES.keys()))
        
        # Generate with Gemini if available
        if self.client:
            return self._generate_with_gemini(video_content, hook_type, include_question, max_length)
        else:
            return self._generate_template_based(video_content, hook_type, include_question, max_length)
    
    def _generate_with_gemini(self,
                             video_content: str,
                             hook_type: str,
                             include_question: bool,
                             max_length: int) -> Dict[str, Any]:
        """Generate caption using Gemini AI."""
        try:
            prompt = f"""
            Create a viral TikTok caption for AFFILIFY (AI-powered affiliate website builder).
            
            Video content: {video_content}
            Hook type: {hook_type}
            
            The caption MUST include:
            1. Compelling hook (first line) - Use {hook_type} style
            2. Value proposition about AFFILIFY
            3. Strong call-to-action directing to Affilify.eu
            4. {('Engagement question' if include_question else 'No question needed')}
            5. Trending hashtags (10-15 tags)
            
            AFFILIFY key features to emphasize:
            - AI builds professional websites in 30 seconds
            - Transforms ugly affiliate links into beautiful landing pages
            - No code or design skills needed
            - Boosts conversion rates dramatically
            - Perfect for affiliate marketers
            
            Hook examples for {hook_type}:
            {json.dumps(self.HOOK_TEMPLATES[hook_type][:2])}
            
            CTA examples:
            {json.dumps(self.CTA_TEMPLATES[:2])}
            
            Trending hashtags to use:
            {' '.join(self.TRENDING_HASHTAGS[:20])}
            
            Requirements:
            - Maximum {max_length} characters total
            - Use emojis strategically (not too many!)
            - Make it scroll-stopping and engaging
            - Focus on benefits, not features
            - Create urgency and FOMO
            - Sound authentic, not salesy
            
            Return as JSON with:
            {{
                "hook": "The opening hook line",
                "body": "Main caption body (2-3 sentences)",
                "cta": "Strong call to action",
                "question": "Engagement question (if requested)",
                "hashtags": ["list", "of", "hashtags"],
                "full_caption": "Complete assembled caption"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8  # Higher temperature for creativity
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            caption_data = json.loads(content)
            logger.info("Generated viral caption with Gemini")
            
            return caption_data
        
        except Exception as e:
            logger.error(f"Failed to generate caption with Gemini: {e}")
            return self._generate_template_based(video_content, hook_type, include_question, max_length)
    
    def _generate_template_based(self,
                                video_content: str,
                                hook_type: str,
                                include_question: bool,
                                max_length: int) -> Dict[str, Any]:
        """Generate caption using templates (fallback)."""
        
        # Select components
        hook = random.choice(self.HOOK_TEMPLATES[hook_type])
        value_prop = random.choice(self.VALUE_PROPS)
        cta = random.choice(self.CTA_TEMPLATES)
        question = random.choice(self.ENGAGEMENT_QUESTIONS) if include_question else ""
        
        # Select hashtags (10-15 tags)
        num_hashtags = random.randint(10, 15)
        hashtags = random.sample(self.TRENDING_HASHTAGS, num_hashtags)
        
        # Assemble caption
        parts = [hook, "", value_prop]
        
        if include_question:
            parts.append("")
            parts.append(question)
        
        parts.append("")
        parts.append(cta)
        parts.append("")
        parts.append(" ".join(hashtags))
        
        full_caption = "\n".join(parts)
        
        # Trim if too long
        if len(full_caption) > max_length:
            # Remove some hashtags
            hashtags = hashtags[:8]
            parts[-1] = " ".join(hashtags)
            full_caption = "\n".join(parts)
        
        return {
            "hook": hook,
            "body": value_prop,
            "cta": cta,
            "question": question,
            "hashtags": hashtags,
            "full_caption": full_caption
        }
    
    def generate_batch_captions(self,
                               video_descriptions: List[str],
                               ensure_variety: bool = True) -> List[Dict[str, Any]]:
        """
        Generate captions for a batch of videos with variety.
        
        Args:
            video_descriptions: List of video content descriptions
            ensure_variety: Whether to ensure different hooks/CTAs
        
        Returns:
            List of caption data dictionaries
        """
        logger.info(f"Generating captions for {len(video_descriptions)} videos")
        
        captions = []
        used_hooks = set()
        used_ctas = set()
        
        hook_types = list(self.HOOK_TEMPLATES.keys())
        
        for i, description in enumerate(video_descriptions):
            # Rotate through hook types for variety
            hook_type = hook_types[i % len(hook_types)]
            
            # Generate caption
            caption = self.generate_viral_caption(
                description,
                hook_type=hook_type,
                include_question=(i % 3 == 0)  # Every 3rd video has a question
            )
            
            # Ensure variety if requested
            if ensure_variety:
                # If we've used this hook, try another
                attempts = 0
                while caption['hook'] in used_hooks and attempts < 5:
                    caption = self.generate_viral_caption(
                        description,
                        hook_type=random.choice(hook_types)
                    )
                    attempts += 1
                
                used_hooks.add(caption['hook'])
                used_ctas.add(caption['cta'])
            
            captions.append(caption)
        
        logger.info(f"Generated {len(captions)} unique captions")
        return captions
    
    def generate_caption_report(self,
                              captions: List[Dict[str, Any]],
                              output_path: str) -> str:
        """
        Generate a report of all captions for review.
        
        Args:
            captions: List of caption dictionaries
            output_path: Path to save report
        
        Returns:
            Path to generated report
        """
        report_lines = [
            "=" * 80,
            "AFFILIFY TIKTOK - VIRAL CAPTION REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total captions: {len(captions)}",
            "",
            "=" * 80,
            ""
        ]
        
        for i, caption in enumerate(captions, 1):
            report_lines.extend([
                f"CAPTION {i}",
                "-" * 80,
                "",
                caption.get('full_caption', ''),
                "",
                "COMPONENTS:",
                f"  Hook: {caption.get('hook', 'N/A')}",
                f"  CTA: {caption.get('cta', 'N/A')}",
                f"  Question: {caption.get('question', 'N/A')}",
                f"  Hashtags: {len(caption.get('hashtags', []))} tags",
                f"  Length: {len(caption.get('full_caption', ''))} characters",
                "",
                ""
            ])
        
        # Write report
        from pathlib import Path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Caption report generated: {output_path}")
        return output_path


if __name__ == "__main__":
    # Test the caption generator
    logging.basicConfig(level=logging.INFO)
    
    generator = ViralCaptionGenerator()
    
    print("Testing Viral Caption Generator...")
    print("=" * 80)
    
    # Test single caption
    print("\n1. Generating single viral caption...")
    caption = generator.generate_viral_caption(
        "AI-powered website builder transforms ugly affiliate link into beautiful landing page in 30 seconds",
        hook_type="problem_solution"
    )
    
    print("\nGENERATED CAPTION:")
    print("-" * 80)
    print(caption['full_caption'])
    print("-" * 80)
    
    # Test batch
    print("\n2. Generating batch of 5 captions...")
    test_videos = [
        "Quick demo of AFFILIFY creating a website",
        "Before/after comparison of affiliate links",
        "Success story: Made $10k with AFFILIFY",
        "Tutorial: How to use AFFILIFY in 30 seconds",
        "Revealing the secret to high-converting affiliate sites"
    ]
    
    batch_captions = generator.generate_batch_captions(test_videos)
    print(f"Generated {len(batch_captions)} unique captions")
    
    # Generate report
    print("\n3. Generating caption report...")
    report_path = "/tmp/caption_report.txt"
    generator.generate_caption_report(batch_captions, report_path)
    print(f"Report saved to: {report_path}")
    
    print("\n✅ Viral caption generator test complete!")
