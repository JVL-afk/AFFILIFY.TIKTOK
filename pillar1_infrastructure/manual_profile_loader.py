#!/usr/bin/env python3
"""
Manual Profile Loader
======================
This script loads profile mappings from a CSV file instead of using the MultiLogin API.
This is useful when profiles are split across multiple MultiLogin accounts for security.

The CSV file should contain:
- profile_name: Name of the profile (e.g., TIKTOK1)
- profile_uuid: MultiLogin profile UUID
- proxy_host: Proxy hostname
- proxy_port: Proxy port
- proxy_username: Proxy username (session ID)
- proxy_password: Proxy password
- multilogin_account: (Optional) Which MultiLogin account owns this profile
- notes: (Optional) Any notes about the profile

Usage:
    python3 manual_profile_loader.py --csv data/profile_mapping.csv
"""

import os
import sys
import csv
import logging
import argparse
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ManualProfileLoader:
    """
    Loads profile mappings from a CSV file and stores them in the database.
    
    This approach doesn't require API access to MultiLogin accounts.
    """
    
    def __init__(self, csv_path: str, database_path: str):
        """
        Initialize the manual profile loader.
        
        Args:
            csv_path: Path to the CSV file containing profile mappings
            database_path: Path to the SQLite database
        """
        self.csv_path = csv_path
        self.database = Database(database_path)
        
        # Initialize database schema
        self.database.initialize_schema()
        
        self.loaded_profiles: List[Dict[str, Any]] = []
        self.failed_profiles: List[Dict[str, Any]] = []
    
    def validate_csv_file(self) -> bool:
        """
        Validate that the CSV file exists and has the correct format.
        
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(self.csv_path):
            logger.error(f"CSV file not found: {self.csv_path}")
            return False
        
        # Check that file has required columns
        required_columns = [
            'profile_name',
            'profile_uuid',
            'proxy_host',
            'proxy_port',
            'proxy_username',
            'proxy_password'
        ]
        
        try:
            with open(self.csv_path, 'r') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                if not headers:
                    logger.error("CSV file has no headers")
                    return False
                
                missing_columns = [col for col in required_columns if col not in headers]
                
                if missing_columns:
                    logger.error(f"CSV file missing required columns: {', '.join(missing_columns)}")
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return False
    
    def load_profiles_from_csv(self) -> List[Dict[str, Any]]:
        """
        Load profile mappings from the CSV file.
        
        Returns:
            List of profile dictionaries
        """
        logger.info(f"Loading profiles from CSV: {self.csv_path}")
        
        profiles = []
        
        try:
            with open(self.csv_path, 'r') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    # Skip empty rows
                    if not row.get('profile_name') or not row.get('profile_uuid'):
                        logger.warning(f"Skipping empty row {row_num}")
                        continue
                    
                    # Validate required fields
                    required_fields = [
                        'profile_name',
                        'profile_uuid',
                        'proxy_host',
                        'proxy_port',
                        'proxy_username',
                        'proxy_password'
                    ]
                    
                    missing_fields = [field for field in required_fields if not row.get(field)]
                    
                    if missing_fields:
                        logger.warning(f"Row {row_num}: Missing fields {missing_fields}, skipping")
                        continue
                    
                    # Create profile dictionary
                    profile = {
                        'name': row['profile_name'].strip(),
                        'uuid': row['profile_uuid'].strip(),
                        'proxy': {
                            'host': row['proxy_host'].strip(),
                            'port': row['proxy_port'].strip(),
                            'username': row['proxy_username'].strip(),
                            'password': row['proxy_password'].strip()
                        },
                        'multilogin_account': row.get('multilogin_account', '').strip(),
                        'notes': row.get('notes', '').strip()
                    }
                    
                    profiles.append(profile)
                    logger.debug(f"Loaded profile: {profile['name']}")
            
            logger.info(f"✅ Loaded {len(profiles)} profiles from CSV")
            return profiles
        
        except Exception as e:
            logger.error(f"Error loading profiles from CSV: {e}")
            return []
    
    def save_profiles_to_database(self, profiles: List[Dict[str, Any]]):
        """
        Save all profiles to the database.
        
        Args:
            profiles: List of profile dictionaries
        """
        logger.info("Saving profiles to database...")
        
        for profile in profiles:
            try:
                # Check if profile already exists
                existing = self.database.get_profile_by_uuid(profile['uuid'])
                
                if existing:
                    logger.info(f"  Profile {profile['name']} already in database, updating...")
                    # Update existing profile
                    # Note: We'd need to add an update method to the database class
                    # For now, we'll skip duplicates
                    continue
                
                # Add profile to database using the correct method
                profile_data = {
                    'profile_id': profile['uuid'],
                    'profile_name': profile['name'],
                    'proxy_index': len(self.loaded_profiles),  # Use index as proxy assignment
                    'country_code': profile.get('notes', 'XX')[:2],  # Extract country code from notes
                    'timezone': 'UTC',  # Default timezone
                    'browser_type': 'mimic',  # Default browser type
                    'os_type': 'android',  # Default OS type
                    'notes': f"Proxy: {profile['proxy']['host']}:{profile['proxy']['port']}"
                }
                self.database.insert_multilogin_profile(profile_data)
                
                # Also insert proxy assignment
                proxy_data = {
                    'proxy_index': len(self.loaded_profiles),
                    'account_name': profile['name'],
                    'country_code': profile.get('notes', 'XX')[:2].upper(),
                    'host': profile['proxy']['host'],
                    'port': int(profile['proxy']['port']),
                    'username': profile['proxy']['username'],
                    'password': profile['proxy']['password'],
                    'proxy_type': 'mobile',  # Fixed field name
                    'session_id': profile['proxy']['username']  # Use username as session_id
                }
                self.database.insert_proxy_assignment(proxy_data)
                
                self.loaded_profiles.append(profile)
                logger.info(f"  ✓ Saved {profile['name']} to database")
            
            except Exception as e:
                logger.error(f"  ✗ Failed to save {profile['name']}: {e}")
                self.failed_profiles.append({
                    'profile': profile,
                    'error': str(e)
                })
    
    def run(self) -> bool:
        """
        Execute the complete manual profile loading workflow.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 70)
        logger.info("MANUAL PROFILE LOADER - STARTING")
        logger.info("=" * 70)
        
        try:
            # Step 1: Validate CSV file
            if not self.validate_csv_file():
                logger.error("CSV file validation failed")
                return False
            
            # Step 2: Load profiles from CSV
            profiles = self.load_profiles_from_csv()
            
            if not profiles:
                logger.error("No profiles loaded from CSV")
                return False
            
            # Step 3: Save to database
            self.save_profiles_to_database(profiles)
            
            # Print summary
            logger.info("=" * 70)
            logger.info("PROFILE LOADING COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Total profiles in CSV: {len(profiles)}")
            logger.info(f"Successfully loaded: {len(self.loaded_profiles)}")
            logger.info(f"Failed: {len(self.failed_profiles)}")
            
            if self.failed_profiles:
                logger.warning("\nFailed profiles:")
                for failed in self.failed_profiles:
                    logger.warning(f"  - {failed['profile']['name']}: {failed['error']}")
            
            logger.info("=" * 70)
            
            return len(self.loaded_profiles) > 0
        
        except Exception as e:
            logger.error(f"Profile loading failed: {e}", exc_info=True)
            return False


def main():
    """Main entry point for the manual profile loader."""
    parser = argparse.ArgumentParser(
        description="Load profile mappings from CSV file"
    )
    parser.add_argument(
        '--csv',
        default='data/profile_mapping.csv',
        help='Path to CSV file containing profile mappings (default: data/profile_mapping.csv)'
    )
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to .env file (default: .env)'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv(args.env_file)
    
    # Get database path
    database_path = os.getenv('DATABASE_PATH', 'data/affilify_system.db')
    
    # Create and run loader
    loader = ManualProfileLoader(args.csv, database_path)
    success = loader.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
