"""
Report Generator
================
This module generates comprehensive daily reports on system performance.

Reports include:
1. Daily performance summary
2. Top-performing content
3. Optimization recommendations
4. Raw video requests
5. System health status
"""

import os
import sys
import logging
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Database

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates comprehensive reports on system performance.
    
    Creates both JSON and human-readable reports.
    """
    
    def __init__(self, database_path: str):
        """
        Initialize the report generator.
        
        Args:
            database_path: Path to the SQLite database
        """
        self.database = Database(database_path)
        
        logger.info("ReportGenerator initialized")
    
    def generate_daily_summary(self) -> Dict[str, Any]:
        """
        Generate a daily performance summary.
        
        Returns:
            Dictionary containing daily stats
        """
        logger.info("Generating daily summary...")
        
        # TODO: Query database for today's stats
        
        summary = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'videos_posted': 0,
            'total_views': 0,
            'total_likes': 0,
            'total_comments': 0,
            'total_shares': 0,
            'average_engagement_rate': 0.0,
            'accounts_active': 0,
            'accounts_flagged': 0
        }
        
        logger.info(f"Daily summary: {summary['videos_posted']} videos posted, "
                   f"{summary['total_views']} total views")
        
        return summary
    
    def get_top_performing_videos(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top-performing videos from the last 7 days.
        
        Args:
            limit: Number of top videos to return
        
        Returns:
            List of video performance dictionaries
        """
        logger.info(f"Getting top {limit} performing videos...")
        
        # TODO: Query database for top videos
        
        top_videos = []
        
        logger.info(f"Found {len(top_videos)} top-performing videos")
        return top_videos
    
    def get_optimization_recommendations(self) -> List[str]:
        """
        Get the latest optimization recommendations.
        
        Returns:
            List of recommendation strings
        """
        logger.info("Loading optimization recommendations...")
        
        # Load latest optimization report
        reports_dir = Path("/home/ubuntu/affilify_tiktok_system/data/reports")
        
        if not reports_dir.exists():
            logger.warning("Reports directory not found")
            return []
        
        # Find latest optimization report
        report_files = list(reports_dir.glob("optimization_report_*.json"))
        
        if not report_files:
            logger.warning("No optimization reports found")
            return []
        
        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_report, 'r') as f:
            report_data = json.load(f)
        
        recommendations = report_data.get('recommendations', [])
        
        logger.info(f"Loaded {len(recommendations)} recommendations")
        return recommendations
    
    def generate_raw_video_requests(self) -> List[Dict[str, Any]]:
        """
        Generate requests for new raw videos based on performance data.
        
        Returns:
            List of video request dictionaries
        """
        logger.info("Generating raw video requests...")
        
        # TODO: Analyze which features need more content
        
        requests = [
            {
                'feature': 'Create Website',
                'priority': 'high',
                'reason': 'Top-performing feature with high engagement',
                'suggested_focus': 'Show advanced customization options'
            },
            {
                'feature': 'AI Chatbot',
                'priority': 'medium',
                'reason': 'Trending topic with growing interest',
                'suggested_focus': 'Demonstrate real-time conversation examples'
            }
        ]
        
        logger.info(f"Generated {len(requests)} video requests")
        return requests
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Check the overall health of the system.
        
        Returns:
            Dictionary containing health status
        """
        logger.info("Checking system health...")
        
        # TODO: Check various system components
        
        health = {
            'status': 'healthy',  # 'healthy', 'warning', 'critical'
            'database_size_mb': 0,
            'profiles_active': 0,
            'profiles_flagged': 0,
            'last_post_time': None,
            'issues': []
        }
        
        logger.info(f"System status: {health['status']}")
        return health
    
    def generate_full_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive daily report.
        
        Returns:
            Dictionary containing the full report
        """
        logger.info("=" * 80)
        logger.info("GENERATING FULL DAILY REPORT")
        logger.info("=" * 80)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_date': datetime.now().strftime("%Y-%m-%d"),
            'daily_summary': self.generate_daily_summary(),
            'top_performing_videos': self.get_top_performing_videos(),
            'optimization_recommendations': self.get_optimization_recommendations(),
            'raw_video_requests': self.generate_raw_video_requests(),
            'system_health': self.check_system_health()
        }
        
        logger.info("=" * 80)
        logger.info("FULL REPORT COMPLETE")
        logger.info("=" * 80)
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_dir: str) -> Path:
        """
        Save report to file.
        
        Args:
            report: Report dictionary
            output_dir: Output directory path
        
        Returns:
            Path to saved report file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_path / f"daily_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Report saved to: {report_file}")
        
        return report_file
    
    def generate_human_readable_report(self, report: Dict[str, Any]) -> str:
        """
        Generate a human-readable text version of the report.
        
        Args:
            report: Report dictionary
        
        Returns:
            Formatted text report
        """
        summary = report['daily_summary']
        health = report['system_health']
        
        text = f"""
{'=' * 80}
AFFILIFY TIKTOK SYSTEM - DAILY REPORT
{'=' * 80}

Report Date: {report['report_date']}
Generated: {report['generated_at']}

{'=' * 80}
DAILY PERFORMANCE SUMMARY
{'=' * 80}

Videos Posted: {summary['videos_posted']}
Total Views: {summary['total_views']:,}
Total Likes: {summary['total_likes']:,}
Total Comments: {summary['total_comments']:,}
Total Shares: {summary['total_shares']:,}
Average Engagement Rate: {summary['average_engagement_rate']:.2f}%

Accounts Active: {summary['accounts_active']}
Accounts Flagged: {summary['accounts_flagged']}

{'=' * 80}
TOP PERFORMING VIDEOS
{'=' * 80}

"""
        
        for idx, video in enumerate(report['top_performing_videos'][:5], 1):
            text += f"{idx}. {video.get('feature', 'Unknown')} - {video.get('views', 0):,} views\n"
        
        text += f"""
{'=' * 80}
OPTIMIZATION RECOMMENDATIONS
{'=' * 80}

"""
        
        for idx, rec in enumerate(report['optimization_recommendations'], 1):
            text += f"{idx}. {rec}\n"
        
        text += f"""
{'=' * 80}
RAW VIDEO REQUESTS
{'=' * 80}

"""
        
        for req in report['raw_video_requests']:
            text += f"Feature: {req['feature']} (Priority: {req['priority']})\n"
            text += f"  Reason: {req['reason']}\n"
            text += f"  Focus: {req['suggested_focus']}\n\n"
        
        text += f"""
{'=' * 80}
SYSTEM HEALTH
{'=' * 80}

Status: {health['status'].upper()}
Database Size: {health['database_size_mb']} MB
Active Profiles: {health['profiles_active']}
Flagged Profiles: {health['profiles_flagged']}

{'=' * 80}
"""
        
        return text


if __name__ == "__main__":
    # Test the report generator
    logging.basicConfig(level=logging.INFO)
    
    print("ReportGenerator module loaded successfully!")
    print("=" * 80)
    print("This module generates comprehensive daily reports.")
    print("=" * 80)
