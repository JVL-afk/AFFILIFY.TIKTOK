"""
Database Schema and Management
===============================
This module defines the complete database schema for the Affilify TikTok
Content Distribution System. It uses SQLite for simplicity and portability.

The database tracks:
- MultiLogin profiles
- Proxy assignments
- TikTok accounts
- Posted videos
- Performance metrics
- Trend data
- Optimization results
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    """
    Database manager for the Affilify TikTok system.
    
    This class handles all database operations including initialization,
    queries, and updates.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def initialize_schema(self):
        """
        Create all database tables if they don't exist.
        
        This method is idempotent - it can be called multiple times safely.
        """
        logger.info("Initializing database schema...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table 1: MultiLogin Profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS multilogin_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT UNIQUE NOT NULL,
                    profile_name TEXT NOT NULL,
                    proxy_index INTEGER NOT NULL,
                    country_code TEXT NOT NULL,
                    timezone TEXT NOT NULL,
                    browser_type TEXT NOT NULL,
                    os_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used_at TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    notes TEXT
                )
            """)
            
            # Table 2: Proxy Assignments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proxy_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proxy_index INTEGER UNIQUE NOT NULL,
                    account_name TEXT NOT NULL,
                    country_code TEXT NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    proxy_type TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    assigned_to_profile_id TEXT,
                    status TEXT DEFAULT 'available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (assigned_to_profile_id) REFERENCES multilogin_profiles(profile_id)
                )
            """)
            
            # Table 3: TikTok Accounts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tiktok_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    profile_id TEXT UNIQUE NOT NULL,
                    account_status TEXT DEFAULT 'active',
                    total_posts INTEGER DEFAULT 0,
                    total_views INTEGER DEFAULT 0,
                    total_likes INTEGER DEFAULT 0,
                    total_comments INTEGER DEFAULT 0,
                    total_shares INTEGER DEFAULT 0,
                    last_post_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    banned_at TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (profile_id) REFERENCES multilogin_profiles(profile_id)
                )
            """)
            
            # Table 4: Posted Videos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posted_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT UNIQUE NOT NULL,
                    tiktok_account_id INTEGER NOT NULL,
                    profile_id TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    processed_filename TEXT NOT NULL,
                    affilify_feature TEXT NOT NULL,
                    caption TEXT NOT NULL,
                    hashtags TEXT NOT NULL,
                    trending_sound_used TEXT,
                    trending_hashtag_used TEXT,
                    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    views_24h INTEGER DEFAULT 0,
                    likes_24h INTEGER DEFAULT 0,
                    comments_24h INTEGER DEFAULT 0,
                    shares_24h INTEGER DEFAULT 0,
                    views_7d INTEGER DEFAULT 0,
                    likes_7d INTEGER DEFAULT 0,
                    comments_7d INTEGER DEFAULT 0,
                    shares_7d INTEGER DEFAULT 0,
                    last_scraped_at TIMESTAMP,
                    tiktok_url TEXT,
                    status TEXT DEFAULT 'posted',
                    FOREIGN KEY (tiktok_account_id) REFERENCES tiktok_accounts(id),
                    FOREIGN KEY (profile_id) REFERENCES multilogin_profiles(profile_id)
                )
            """)
            
            # Table 5: Trending Hashtags
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trending_hashtags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hashtag TEXT NOT NULL,
                    view_count BIGINT,
                    post_count BIGINT,
                    trending_score REAL,
                    category TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Table 6: Trending Sounds
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trending_sounds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sound_id TEXT UNIQUE NOT NULL,
                    sound_name TEXT NOT NULL,
                    artist TEXT,
                    use_count BIGINT,
                    trending_score REAL,
                    category TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Table 7: Optimization Results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS optimization_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    optimization_date DATE NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    best_performing_feature TEXT,
                    best_performing_hashtag TEXT,
                    best_performing_time_slot TEXT,
                    best_performing_caption_style TEXT,
                    total_views INTEGER,
                    total_engagement INTEGER,
                    conversion_rate REAL,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 8: System Logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    error_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 9: Account Health History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS account_health_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    health_check_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    posts_today INTEGER DEFAULT 0,
                    last_error TEXT,
                    response_time_ms INTEGER,
                    FOREIGN KEY (profile_id) REFERENCES multilogin_profiles(profile_id)
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_posted_videos_account 
                ON posted_videos(tiktok_account_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_posted_videos_feature 
                ON posted_videos(affilify_feature)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_posted_videos_posted_at 
                ON posted_videos(posted_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_trending_hashtags_score 
                ON trending_hashtags(trending_score DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_trending_sounds_score 
                ON trending_sounds(trending_score DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_account_health_profile 
                ON account_health_history(profile_id, health_check_at)
            """)
            
            logger.info("Database schema initialized successfully")
    
    def insert_multilogin_profile(self, profile_data: Dict[str, Any]) -> int:
        """
        Insert a new MultiLogin profile record.
        
        Args:
            profile_data: Dictionary containing profile information
        
        Returns:
            ID of the inserted record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO multilogin_profiles 
                (profile_id, profile_name, proxy_index, country_code, timezone, 
                 browser_type, os_type, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_data['profile_id'],
                profile_data['profile_name'],
                profile_data['proxy_index'],
                profile_data['country_code'],
                profile_data['timezone'],
                profile_data['browser_type'],
                profile_data['os_type'],
                profile_data.get('notes', '')
            ))
            return cursor.lastrowid
    
    def insert_proxy_assignment(self, proxy_data: Dict[str, Any]) -> int:
        """
        Insert a new proxy assignment record.
        
        Args:
            proxy_data: Dictionary containing proxy information
        
        Returns:
            ID of the inserted record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO proxy_assignments 
                (proxy_index, account_name, country_code, host, port, username, 
                 password, proxy_type, session_id, assigned_to_profile_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proxy_data['proxy_index'],
                proxy_data['account_name'],
                proxy_data['country_code'],
                proxy_data['host'],
                proxy_data['port'],
                proxy_data['username'],
                proxy_data['password'],
                proxy_data['proxy_type'],
                proxy_data['session_id'],
                proxy_data.get('assigned_to_profile_id'),
                proxy_data.get('status', 'available')
            ))
            return cursor.lastrowid
    
    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """
        Get all MultiLogin profiles.
        
        Returns:
            List of profile dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM multilogin_profiles ORDER BY id")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific profile by its ID.
        
        Args:
            profile_id: MultiLogin profile ID
        
        Returns:
            Profile dictionary or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM multilogin_profiles WHERE profile_id = ?",
                (profile_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_profile_by_uuid(self, profile_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific profile by its UUID.
        
        Args:
            profile_uuid: MultiLogin profile UUID
        
        Returns:
            Profile dictionary or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM multilogin_profiles WHERE profile_id = ?",
                (profile_uuid,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_profile_by_name(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific profile by its name.
        
        Args:
            profile_name: Profile name
        
        Returns:
            Profile dictionary or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM multilogin_profiles WHERE profile_name = ?",
                (profile_name,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_profile_status(self, profile_id: str, status: str):
        """
        Update the status of a profile.
        
        Args:
            profile_id: MultiLogin profile ID
            status: New status (e.g., 'active', 'banned', 'retired')
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE multilogin_profiles 
                SET status = ?, last_used_at = CURRENT_TIMESTAMP
                WHERE profile_id = ?
            """, (status, profile_id))
    
    def log_system_event(self, level: str, component: str, message: str, 
                        error_details: Optional[str] = None):
        """
        Log a system event to the database.
        
        Args:
            level: Log level (INFO, WARNING, ERROR, CRITICAL)
            component: Component name (e.g., 'pillar1', 'pillar2')
            message: Log message
            error_details: Optional error details
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (log_level, component, message, error_details)
                VALUES (?, ?, ?, ?)
            """, (level, component, message, error_details))
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall system statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Profile statistics
            cursor.execute("SELECT COUNT(*) as total FROM multilogin_profiles")
            stats['total_profiles'] = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT COUNT(*) as active 
                FROM multilogin_profiles 
                WHERE status = 'active'
            """)
            stats['active_profiles'] = cursor.fetchone()['active']
            
            # Video statistics
            cursor.execute("SELECT COUNT(*) as total FROM posted_videos")
            stats['total_videos_posted'] = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT SUM(views_24h) as total_views 
                FROM posted_videos
            """)
            result = cursor.fetchone()
            stats['total_views'] = result['total_views'] or 0
            
            cursor.execute("""
                SELECT SUM(likes_24h) as total_likes 
                FROM posted_videos
            """)
            result = cursor.fetchone()
            stats['total_likes'] = result['total_likes'] or 0
            
            return stats


if __name__ == "__main__":
    # Test the database
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    test_db_path = "/tmp/test_affilify.db"
    
    # Remove old test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = Database(test_db_path)
    db.initialize_schema()
    
    # Test inserting a profile
    test_profile = {
        'profile_id': 'test-profile-001',
        'profile_name': 'Test Profile 1',
        'proxy_index': 0,
        'country_code': 'us',
        'timezone': 'America/New_York',
        'browser_type': 'mimic',
        'os_type': 'windows',
        'notes': 'Test profile'
    }
    
    profile_id = db.insert_multilogin_profile(test_profile)
    print(f"Inserted profile with ID: {profile_id}")
    
    # Test retrieving the profile
    retrieved = db.get_profile_by_id('test-profile-001')
    print(f"Retrieved profile: {retrieved}")
    
    # Test statistics
    stats = db.get_statistics()
    print(f"Statistics: {stats}")
    
    print("\nDatabase test completed successfully!")
