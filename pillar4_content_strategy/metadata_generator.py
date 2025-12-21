"""
Metadata Generator
==================
This module generates optimized TikTok captions, hashtags, and descriptions
using Gemini AI and trend intelligence.

Key functions:
1. Generate engaging captions that incorporate trending elements
2. Select optimal hashtags based on current trends
3. Create calls-to-action that drive traffic to Affilify
4. Generate 60 unique variations to avoid duplicate content detection
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


class MetadataGenerator:
    """
    Generates optimized metadata for TikTok posts.
    
    Uses trend intelligence and Gemini AI to create captions,
    hashtags, and descriptions that maximize engagement.
    """
    
    # Base hashtags (always included)
    BASE_HASHTAGS = [
        "#affilify",
        "#affiliatemarketing",
        "#makemoneyonline",
        "#sidehustle",
        "#entrepreneur"
    ]
    
    # Call-to-action templates
    CTA_TEMPLATES = [
        "Link in bio to get started! 🚀",
        "Try it free at affilify.eu 💎",
        "Check out affilify.eu for more! ✨",
        "Visit affilify.eu to learn more 🔥",
        "Get started today → affilify.eu 💪",
        "Transform your business → affilify.eu 🎯",
        "Start your free trial at affilify.eu 🌟",
        "Discover more at affilify.eu 💡"
    ]
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the metadata generator.
        
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
                logger.info("Gemini API client initialized for metadata generation")
            except ImportError:
                logger.error("OpenAI package not installed")
        
        logger.info("MetadataGenerator initialized")
    
    def generate_caption_with_gemini(self, 
                                    affilify_feature: str,
                                    trending_hashtags: List[str],
                                    variation_index: int = 0) -> str:
        """
        Generate an engaging caption using Gemini AI.
        
        Args:
            affilify_feature: The Affilify feature being showcased
            trending_hashtags: List of currently trending hashtags
            variation_index: Index for creating unique variations
        
        Returns:
            Generated caption
        """
        if not self.client:
            # Fallback to template-based generation
            return self._generate_caption_template(affilify_feature, variation_index)
        
        try:
            # Create a prompt for Gemini
            prompt = f"""
Generate an engaging TikTok caption for a video showcasing the "{affilify_feature}" feature of Affilify,
an affiliate marketing platform.

The caption should:
1. Be concise (max 150 characters)
2. Include an emoji
3. Create curiosity or provide value
4. Sound natural and authentic (not salesy)
5. Incorporate one of these trending contexts if relevant: {', '.join(trending_hashtags[:5])}

Generate variation #{variation_index + 1} to ensure uniqueness.

Return ONLY the caption text, nothing else.
"""
            
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert TikTok content creator who writes engaging, authentic captions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.9,  # Higher temperature for more variation
                max_tokens=100
            )
            
            caption = response.choices[0].message.content.strip()
            logger.info(f"Generated caption with Gemini: {caption[:50]}...")
            return caption
        
        except Exception as e:
            logger.error(f"Gemini caption generation failed: {e}")
            return self._generate_caption_template(affilify_feature, variation_index)
    
    def _generate_caption_template(self, affilify_feature: str, variation_index: int = 0) -> str:
        """
        Generate a caption using templates (fallback method).
        
        Args:
            affilify_feature: The Affilify feature
            variation_index: Index for variation
        
        Returns:
            Generated caption
        """
        templates = [
            f"🚀 Game-changer alert: {affilify_feature}",
            f"💎 This {affilify_feature} feature is incredible",
            f"✨ {affilify_feature} made easy",
            f"🔥 You need to see this {affilify_feature} feature",
            f"💪 Level up with {affilify_feature}",
            f"🎯 {affilify_feature} just got better",
            f"⚡ {affilify_feature} in action",
            f"🌟 Discover {affilify_feature}",
        ]
        
        # Select template based on variation index
        template = templates[variation_index % len(templates)]
        return template
    
    def select_optimal_hashtags(self,
                               affilify_feature: str,
                               trending_hashtags: List[str],
                               max_hashtags: int = 15) -> List[str]:
        """
        Select the optimal combination of hashtags.
        
        Args:
            affilify_feature: The Affilify feature
            trending_hashtags: List of currently trending hashtags
            max_hashtags: Maximum number of hashtags to include
        
        Returns:
            List of selected hashtags
        """
        selected = []
        
        # Always include base hashtags
        selected.extend(self.BASE_HASHTAGS)
        
        # Add feature-specific hashtags
        feature_hashtags = self._get_feature_specific_hashtags(affilify_feature)
        selected.extend(feature_hashtags[:3])
        
        # Add trending hashtags (if relevant)
        relevant_trending = self._filter_relevant_trending(trending_hashtags, affilify_feature)
        selected.extend(relevant_trending[:max_hashtags - len(selected)])
        
        # Ensure we don't exceed max
        selected = selected[:max_hashtags]
        
        logger.info(f"Selected {len(selected)} hashtags for {affilify_feature}")
        return selected
    
    def _get_feature_specific_hashtags(self, feature: str) -> List[str]:
        """Get hashtags specific to an Affilify feature."""
        feature_map = {
            "Create Website": ["#websitebuilder", "#webdesign", "#landingpage"],
            "Analyze Website": ["#analytics", "#seo", "#webanalytics"],
            "My Websites": ["#dashboard", "#management", "#portfolio"],
            "Advanced Analytics": ["#data", "#metrics", "#businessanalytics"],
            "AI Chatbot": ["#chatbot", "#ai", "#automation"],
            "A/B Testing": ["#abtesting", "#optimization", "#conversion"],
            "Email Marketing": ["#emailmarketing", "#newsletter", "#marketing"],
            "Team Collaboration": ["#teamwork", "#collaboration", "#productivity"],
            "API Management": ["#api", "#developer", "#integration"],
            "Custom Integrations": ["#integration", "#automation", "#tools"],
            "Code Editor": ["#coding", "#developer", "#programming"],
            "Advanced Reporting": ["#reporting", "#businessintelligence", "#data"]
        }
        
        return feature_map.get(feature, ["#business", "#growth", "#success"])
    
    def _filter_relevant_trending(self, trending_hashtags: List[str], feature: str) -> List[str]:
        """Filter trending hashtags for relevance to the feature."""
        # Simple relevance check (can be enhanced with Gemini)
        relevant = []
        
        feature_keywords = {
            "Create Website": ["website", "web", "design", "build", "create"],
            "Analyze Website": ["analytics", "data", "seo", "traffic"],
            "AI Chatbot": ["ai", "chat", "bot", "automation"],
            "Email Marketing": ["email", "marketing", "campaign"],
        }
        
        keywords = feature_keywords.get(feature, ["business", "entrepreneur", "marketing"])
        
        for hashtag in trending_hashtags:
            hashtag_lower = hashtag.lower()
            if any(keyword in hashtag_lower for keyword in keywords):
                relevant.append(hashtag)
        
        return relevant
    
    def generate_complete_metadata(self,
                                   affilify_feature: str,
                                   trending_hashtags: List[str],
                                   variation_index: int = 0) -> Dict[str, Any]:
        """
        Generate complete metadata for a TikTok post.
        
        Args:
            affilify_feature: The Affilify feature being showcased
            trending_hashtags: List of currently trending hashtags
            variation_index: Index for creating unique variations
        
        Returns:
            Dictionary containing all metadata
        """
        logger.info(f"Generating metadata for {affilify_feature} (variation {variation_index + 1})...")
        
        # Generate caption
        caption = self.generate_caption_with_gemini(
            affilify_feature=affilify_feature,
            trending_hashtags=trending_hashtags,
            variation_index=variation_index
        )
        
        # Select hashtags
        hashtags = self.select_optimal_hashtags(
            affilify_feature=affilify_feature,
            trending_hashtags=trending_hashtags
        )
        
        # Select CTA
        cta = random.choice(self.CTA_TEMPLATES)
        
        # Combine into full description
        hashtag_string = " ".join(hashtags)
        full_description = f"{caption}\n\n{cta}\n\n{hashtag_string}"
        
        metadata = {
            'caption': caption,
            'hashtags': hashtags,
            'cta': cta,
            'full_description': full_description,
            'affilify_feature': affilify_feature,
            'variation_index': variation_index,
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Generated metadata (length: {len(full_description)} chars)")
        return metadata
    
    def generate_batch_metadata(self,
                               affilify_feature: str,
                               trending_hashtags: List[str],
                               num_variations: int = 60) -> List[Dict[str, Any]]:
        """
        Generate metadata for multiple variations.
        
        Args:
            affilify_feature: The Affilify feature
            trending_hashtags: List of trending hashtags
            num_variations: Number of unique variations to create
        
        Returns:
            List of metadata dictionaries
        """
        logger.info(f"Generating {num_variations} metadata variations for {affilify_feature}...")
        
        metadata_batch = []
        
        for i in range(num_variations):
            metadata = self.generate_complete_metadata(
                affilify_feature=affilify_feature,
                trending_hashtags=trending_hashtags,
                variation_index=i
            )
            
            metadata_batch.append(metadata)
            
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{num_variations} metadata generated")
        
        logger.info(f"✅ Generated {len(metadata_batch)} unique metadata variations")
        return metadata_batch


if __name__ == "__main__":
    # Test the metadata generator
    logging.basicConfig(level=logging.INFO)
    
    print("MetadataGenerator module loaded successfully!")
    print("=" * 80)
    print("This module generates optimized TikTok metadata using Gemini AI.")
    print("=" * 80)
