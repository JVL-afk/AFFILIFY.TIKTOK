"""
Gemini AI Trend Analyzer
=========================
This module uses Google's Gemini 2.5 Flash API to analyze TikTok trends
and map them to Affilify features.

Key functions:
1. Analyze trending hashtags and identify opportunities
2. Predict which trends will grow
3. Map trends to specific Affilify features
4. Generate content strategy recommendations
"""

import os
import sys
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class GeminiTrendAnalyzer:
    """
    Uses Gemini AI to analyze TikTok trends and generate insights.
    
    This class provides intelligent analysis of trending content
    to inform the content strategy for Affilify promotion.
    """
    
    # Affilify features (from research)
    AFFILIFY_FEATURES = [
        {
            "name": "Create Website",
            "description": "Build professional affiliate websites with AI-powered tools",
            "keywords": ["website", "build", "create", "design", "landing page", "site builder"]
        },
        {
            "name": "Analyze Website",
            "description": "Get AI-driven insights on website performance and optimization",
            "keywords": ["analytics", "analyze", "insights", "performance", "SEO", "optimization"]
        },
        {
            "name": "My Websites",
            "description": "Manage multiple affiliate websites from one dashboard",
            "keywords": ["dashboard", "manage", "multiple sites", "portfolio", "organize"]
        },
        {
            "name": "Advanced Analytics",
            "description": "Track conversions, traffic, and revenue with detailed analytics",
            "keywords": ["analytics", "data", "metrics", "tracking", "conversion", "revenue"]
        },
        {
            "name": "AI Chatbot",
            "description": "Engage visitors with an intelligent AI chatbot",
            "keywords": ["chatbot", "AI", "conversation", "engagement", "automation", "support"]
        },
        {
            "name": "A/B Testing",
            "description": "Test different versions of your site to maximize conversions",
            "keywords": ["A/B test", "split test", "experiment", "optimize", "conversion"]
        },
        {
            "name": "Email Marketing",
            "description": "Build and nurture your email list with integrated tools",
            "keywords": ["email", "newsletter", "list building", "email marketing", "campaigns"]
        },
        {
            "name": "Team Collaboration",
            "description": "Work with your team on affiliate projects",
            "keywords": ["team", "collaboration", "workflow", "project management", "teamwork"]
        },
        {
            "name": "API Management",
            "description": "Integrate with external services via powerful APIs",
            "keywords": ["API", "integration", "developer", "automation", "webhook"]
        },
        {
            "name": "Custom Integrations",
            "description": "Connect Affilify with your favorite tools and platforms",
            "keywords": ["integration", "connect", "plugin", "extension", "third-party"]
        },
        {
            "name": "Code Editor",
            "description": "Advanced code editing for custom functionality",
            "keywords": ["code", "developer", "custom", "HTML", "CSS", "JavaScript"]
        },
        {
            "name": "Advanced Reporting",
            "description": "Generate detailed reports on all aspects of your affiliate business",
            "keywords": ["reporting", "reports", "dashboard", "insights", "business intelligence"]
        }
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini analyzer.
        
        Args:
            api_key: Gemini API key (reads from env if not provided)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            logger.warning("No Gemini API key provided - analysis will be limited")
        
        # Initialize Gemini client (when API key is available)
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                # Use OpenAI-compatible API with Gemini endpoint
                self.client = OpenAI(api_key=self.api_key)
                logger.info("Gemini API client initialized")
            except ImportError:
                logger.error("OpenAI package not installed - install with: pip install openai")
        
        logger.info("GeminiTrendAnalyzer initialized")
    
    def analyze_hashtag_relevance(self, hashtags: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze which hashtags are relevant to Affilify features.
        
        Args:
            hashtags: List of trending hashtags
        
        Returns:
            List of hashtag analysis results
        """
        logger.info(f"Analyzing {len(hashtags)} hashtags for Affilify relevance...")
        
        results = []
        
        for hashtag in hashtags:
            # Simple keyword matching (enhanced with Gemini if available)
            relevant_features = []
            
            hashtag_lower = hashtag.lower()
            
            for feature in self.AFFILIFY_FEATURES:
                # Check if any feature keywords match the hashtag
                for keyword in feature['keywords']:
                    if keyword.lower() in hashtag_lower:
                        relevant_features.append({
                            'feature_name': feature['name'],
                            'match_keyword': keyword,
                            'confidence': 0.8  # Simple match confidence
                        })
                        break
            
            if relevant_features:
                results.append({
                    'hashtag': hashtag,
                    'relevant_features': relevant_features,
                    'total_matches': len(relevant_features)
                })
        
        logger.info(f"✅ Found {len(results)} relevant hashtags")
        return results
    
    def generate_content_strategy(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a content strategy based on current trends.
        
        Args:
            trends: Dictionary containing trending hashtags, songs, creators
        
        Returns:
            Content strategy recommendations
        """
        logger.info("Generating content strategy from trends...")
        
        # Analyze hashtags
        hashtag_analysis = self.analyze_hashtag_relevance(
            [h.get('hashtag', '') for h in trends.get('hashtags', [])]
        )
        
        # Generate strategy
        strategy = {
            'generated_at': datetime.now().isoformat(),
            'top_opportunities': [],
            'recommended_features': [],
            'content_ideas': []
        }
        
        # Identify top opportunities
        if hashtag_analysis:
            # Sort by number of matches
            sorted_hashtags = sorted(
                hashtag_analysis,
                key=lambda x: x['total_matches'],
                reverse=True
            )
            
            strategy['top_opportunities'] = sorted_hashtags[:10]
            
            # Extract most relevant features
            feature_counts = {}
            for item in hashtag_analysis:
                for feature_match in item['relevant_features']:
                    feature_name = feature_match['feature_name']
                    feature_counts[feature_name] = feature_counts.get(feature_name, 0) + 1
            
            # Sort features by frequency
            sorted_features = sorted(
                feature_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            strategy['recommended_features'] = [
                {'feature': name, 'trend_matches': count}
                for name, count in sorted_features[:5]
            ]
        
        # Generate content ideas (simple version - enhanced with Gemini if available)
        if strategy['recommended_features']:
            for feature_data in strategy['recommended_features'][:3]:
                feature_name = feature_data['feature']
                
                # Find the feature details
                feature_info = next(
                    (f for f in self.AFFILIFY_FEATURES if f['name'] == feature_name),
                    None
                )
                
                if feature_info:
                    strategy['content_ideas'].append({
                        'feature': feature_name,
                        'idea': f"Create a video showcasing {feature_name}: {feature_info['description']}",
                        'trending_context': f"Aligns with {feature_data['trend_matches']} current trends"
                    })
        
        logger.info(f"✅ Generated strategy with {len(strategy['content_ideas'])} content ideas")
        return strategy
    
    def analyze_with_gemini(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """
        Use Gemini AI to analyze data with a custom prompt.
        
        Args:
            prompt: The analysis prompt
            model: Gemini model to use
        
        Returns:
            Gemini's response
        """
        if not self.client:
            logger.warning("Gemini client not available - returning placeholder")
            return "Gemini analysis not available (API key not configured)"
        
        try:
            logger.info("Sending request to Gemini API...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in TikTok trends and affiliate marketing strategy."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            logger.info("✅ Received Gemini response")
            return result
        
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return f"Error: {e}"
    
    def generate_advanced_strategy_with_gemini(self, trends: Dict[str, Any]) -> str:
        """
        Use Gemini to generate an advanced content strategy.
        
        Args:
            trends: Dictionary containing trend data
        
        Returns:
            Gemini's strategic analysis
        """
        # Prepare the prompt
        hashtags_str = ", ".join([h.get('hashtag', '') for h in trends.get('hashtags', [])[:20]])
        
        prompt = f"""
Analyze these trending TikTok hashtags and create a content strategy for promoting Affilify, 
an affiliate marketing platform with these features:

{json.dumps([{'name': f['name'], 'description': f['description']} for f in self.AFFILIFY_FEATURES], indent=2)}

Trending hashtags: {hashtags_str}

Please provide:
1. Which Affilify features align best with current trends
2. Specific content ideas that leverage these trends
3. Recommended posting strategy (timing, frequency)
4. Predicted trend longevity (which trends will last vs. fade quickly)

Format your response as actionable recommendations.
"""
        
        return self.analyze_with_gemini(prompt)


if __name__ == "__main__":
    # Test the Gemini analyzer
    logging.basicConfig(level=logging.INFO)
    
    print("GeminiTrendAnalyzer module loaded successfully!")
    print("=" * 80)
    print("This module uses Gemini AI to analyze TikTok trends.")
    print("=" * 80)
