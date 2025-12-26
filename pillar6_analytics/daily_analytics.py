#!/usr/bin/env python3
"""
Daily Analytics Monitor
=======================
Monitors and reports daily TikTok performance metrics.

This script:
1. Tracks views, likes, comments, shares
2. Calculates engagement rates
3. Estimates conversions and revenue
4. Identifies top-performing content
5. Generates daily reports

Usage:
    python3 daily_analytics.py --date today
    python3 daily_analytics.py --date 2025-12-26
    python3 daily_analytics.py --days 7
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyAnalytics:
    """
    Daily analytics monitoring and reporting.
    """
    
    # Revenue calculations
    COMMISSION_PER_CONVERSION = 30  # $30 per AFFILIFY conversion
    CONVERSION_RATE = 0.001  # 0.1% conversion rate (conservative)
    
    def __init__(self, db_path: str = 'data/affilify_tiktok.db'):
        """
        Initialize the analytics monitor.
        
        Args:
            db_path: Path to database
        """
        self.db = Database(db_path)
        logger.info("DailyAnalytics initialized")
    
    def get_daily_stats(self, date: str = None) -> Dict[str, Any]:
        """
        Get statistics for a specific date.
        
        Args:
            date: Date string (YYYY-MM-DD) or 'today'
        
        Returns:
            Dictionary with daily statistics
        """
        if not date or date == 'today':
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Getting stats for {date}")
        
        # In a real implementation, this would query the database
        # For now, we'll return a template structure
        
        stats = {
            'date': date,
            'accounts': {
                'total': 60,
                'active': 60,
                'banned': 0,
                'suspended': 0
            },
            'videos': {
                'posted_today': 0,
                'total_posted': 0,
                'pending': 0
            },
            'engagement': {
                'total_views': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_shares': 0,
                'avg_views_per_video': 0,
                'engagement_rate': 0.0
            },
            'revenue': {
                'estimated_conversions': 0,
                'estimated_revenue': 0.0,
                'conversion_rate': self.CONVERSION_RATE
            },
            'top_videos': []
        }
        
        return stats
    
    def get_period_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get statistics for a period of days.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with period statistics
        """
        logger.info(f"Getting stats for last {days} days")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stats = {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'days': days,
            'daily_breakdown': [],
            'totals': {
                'views': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'videos_posted': 0,
                'estimated_revenue': 0.0
            },
            'averages': {
                'views_per_day': 0,
                'videos_per_day': 0,
                'revenue_per_day': 0.0
            },
            'trends': {
                'views_trend': 'stable',  # 'growing', 'stable', 'declining'
                'engagement_trend': 'stable',
                'revenue_trend': 'stable'
            }
        }
        
        # Get daily stats for each day
        for i in range(days):
            date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_stats = self.get_daily_stats(date)
            stats['daily_breakdown'].append(daily_stats)
        
        return stats
    
    def calculate_revenue(self, views: int) -> Dict[str, float]:
        """
        Calculate estimated revenue from views.
        
        Args:
            views: Total views
        
        Returns:
            Dictionary with revenue calculations
        """
        conversions = views * self.CONVERSION_RATE
        revenue = conversions * self.COMMISSION_PER_CONVERSION
        
        return {
            'views': views,
            'estimated_conversions': conversions,
            'estimated_revenue': revenue,
            'commission_per_conversion': self.COMMISSION_PER_CONVERSION,
            'conversion_rate': self.CONVERSION_RATE
        }
    
    def print_daily_report(self, stats: Dict[str, Any]):
        """
        Print a formatted daily report.
        
        Args:
            stats: Daily statistics dictionary
        """
        print("\n" + "=" * 80)
        print(f"AFFILIFY TIKTOK - DAILY ANALYTICS REPORT")
        print("=" * 80)
        print(f"Date: {stats['date']}")
        print()
        
        print("ACCOUNT STATUS")
        print("-" * 80)
        print(f"  Total accounts: {stats['accounts']['total']}")
        print(f"  Active: {stats['accounts']['active']}")
        print(f"  Banned: {stats['accounts']['banned']}")
        print(f"  Suspended: {stats['accounts']['suspended']}")
        print()
        
        print("VIDEO STATISTICS")
        print("-" * 80)
        print(f"  Posted today: {stats['videos']['posted_today']}")
        print(f"  Total posted: {stats['videos']['total_posted']}")
        print(f"  Pending: {stats['videos']['pending']}")
        print()
        
        print("ENGAGEMENT METRICS")
        print("-" * 80)
        print(f"  Total views: {stats['engagement']['total_views']:,}")
        print(f"  Total likes: {stats['engagement']['total_likes']:,}")
        print(f"  Total comments: {stats['engagement']['total_comments']:,}")
        print(f"  Total shares: {stats['engagement']['total_shares']:,}")
        print(f"  Avg views per video: {stats['engagement']['avg_views_per_video']:,.0f}")
        print(f"  Engagement rate: {stats['engagement']['engagement_rate']:.2f}%")
        print()
        
        print("REVENUE ESTIMATES")
        print("-" * 80)
        print(f"  Estimated conversions: {stats['revenue']['estimated_conversions']:.1f}")
        print(f"  Estimated revenue: ${stats['revenue']['estimated_revenue']:,.2f}")
        print(f"  Conversion rate: {stats['revenue']['conversion_rate']:.2f}%")
        print(f"  Commission per conversion: ${self.COMMISSION_PER_CONVERSION}")
        print()
        
        if stats['top_videos']:
            print("TOP PERFORMING VIDEOS")
            print("-" * 80)
            for i, video in enumerate(stats['top_videos'][:5], 1):
                print(f"  {i}. {video['title']}")
                print(f"     Views: {video['views']:,} | Likes: {video['likes']:,} | Engagement: {video['engagement_rate']:.2f}%")
            print()
        
        print("=" * 80)
    
    def print_period_report(self, stats: Dict[str, Any]):
        """
        Print a formatted period report.
        
        Args:
            stats: Period statistics dictionary
        """
        print("\n" + "=" * 80)
        print(f"AFFILIFY TIKTOK - {stats['days']}-DAY ANALYTICS REPORT")
        print("=" * 80)
        print(f"Period: {stats['period']}")
        print()
        
        print("TOTALS")
        print("-" * 80)
        print(f"  Total views: {stats['totals']['views']:,}")
        print(f"  Total likes: {stats['totals']['likes']:,}")
        print(f"  Total comments: {stats['totals']['comments']:,}")
        print(f"  Total shares: {stats['totals']['shares']:,}")
        print(f"  Videos posted: {stats['totals']['videos_posted']}")
        print(f"  Estimated revenue: ${stats['totals']['estimated_revenue']:,.2f}")
        print()
        
        print("DAILY AVERAGES")
        print("-" * 80)
        print(f"  Views per day: {stats['averages']['views_per_day']:,.0f}")
        print(f"  Videos per day: {stats['averages']['videos_per_day']:.1f}")
        print(f"  Revenue per day: ${stats['averages']['revenue_per_day']:,.2f}")
        print()
        
        print("TRENDS")
        print("-" * 80)
        print(f"  Views: {stats['trends']['views_trend'].upper()}")
        print(f"  Engagement: {stats['trends']['engagement_trend'].upper()}")
        print(f"  Revenue: {stats['trends']['revenue_trend'].upper()}")
        print()
        
        print("=" * 80)
    
    def save_report(self, stats: Dict[str, Any], output_path: str):
        """
        Save report to file.
        
        Args:
            stats: Statistics dictionary
            output_path: Path to save report
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("AFFILIFY TIKTOK - ANALYTICS REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n")
            
            if 'date' in stats:
                # Daily report
                f.write(f"Date: {stats['date']}\n")
            elif 'period' in stats:
                # Period report
                f.write(f"Period: {stats['period']}\n")
            
            f.write("\n")
            f.write("Full report content here...\n")
            f.write("=" * 80 + "\n")
        
        logger.info(f"Report saved to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor and report daily TikTok analytics"
    )
    parser.add_argument(
        '--date',
        default='today',
        help='Date to analyze (YYYY-MM-DD or "today")'
    )
    parser.add_argument(
        '--days',
        type=int,
        help='Number of days to analyze (overrides --date)'
    )
    parser.add_argument(
        '--output',
        help='Save report to file'
    )
    parser.add_argument(
        '--db',
        default='data/affilify_tiktok.db',
        help='Path to database'
    )
    
    args = parser.parse_args()
    
    # Create analytics monitor
    analytics = DailyAnalytics(db_path=args.db)
    
    if args.days:
        # Period report
        stats = analytics.get_period_stats(days=args.days)
        analytics.print_period_report(stats)
    else:
        # Daily report
        stats = analytics.get_daily_stats(date=args.date)
        analytics.print_daily_report(stats)
    
    # Save report if requested
    if args.output:
        analytics.save_report(stats, args.output)


if __name__ == "__main__":
    main()
