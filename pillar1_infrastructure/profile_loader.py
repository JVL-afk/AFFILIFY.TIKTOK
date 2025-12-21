"""
MultiLogin Profile Loader
==========================
This script loads existing MultiLogin profiles (instead of creating new ones).
It extracts profile UUIDs from the MultiLogin account and maps them to proxy credentials.

This script:
1. Searches for all existing TikTok profiles in MultiLogin
2. Extracts their UUIDs and metadata
3. Maps each profile to a proxy from the proxy list
4. Stores all profile information in the database
5. Validates the setup

This is used when you already have MultiLogin profiles created manually.
"""

import os
import sys
import logging
import argparse
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pillar1_infrastructure.proxy_parser import ProxyParser, ProxyCredentials
from pillar1_infrastructure.multilogin_client import MultiLoginClient
from shared.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProfileLoader:
    """
    Loads existing MultiLogin profiles and maps them to proxies.
    
    This class handles the complete workflow of:
    1. Loading proxy credentials
    2. Searching for existing profiles in MultiLogin
    3. Mapping profiles to proxies
    4. Storing results in database
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the profile loader.
        
        Args:
            config: Configuration dictionary containing all necessary settings
        """
        self.config = config
        
        # Initialize components
        self.proxy_parser = ProxyParser(config['proxy_file_path'])
        self.multilogin_client = MultiLoginClient(
            base_url=config['multilogin_api_base_url'],
            email=config['multilogin_email'],
            password=config['multilogin_password'],
            automation_token=config.get('multilogin_automation_token')
        )
        self.database = Database(config['database_path'])
        
        # Initialize database schema
        self.database.initialize_schema()
        
        self.proxies: List[ProxyCredentials] = []
        self.loaded_profiles: List[Dict[str, Any]] = []
        self.failed_profiles: List[Dict[str, Any]] = []
    
    def load_proxies(self):
        """Load and validate all proxy credentials."""
        logger.info("Loading proxy credentials...")
        
        self.proxies = self.proxy_parser.parse()
        
        # Validate proxies
        valid, errors = self.proxy_parser.validate_all_proxies()
        
        if not valid:
            logger.warning("Proxy validation warnings:")
            for error in errors:
                logger.warning(f"  - {error}")
        
        logger.info(f"Loaded {len(self.proxies)} proxies")
    
    def search_existing_profiles(self) -> List[Dict[str, Any]]:
        """
        Search for all existing TikTok profiles in MultiLogin account.
        
        Returns:
            List of profile dictionaries
        """
        logger.info("Searching for existing TikTok profiles in MultiLogin...")
        
        try:
            # Search for all profiles (MultiLogin API handles pagination internally)
            all_profiles = []
            offset = 0
            limit = 100
            
            while True:
                # Use the search_profiles method from MultiLoginClient
                profiles_batch = self.multilogin_client.search_profiles(
                    query="",  # Empty query to get all profiles
                    limit=limit
                )
                
                if not profiles_batch:
                    break
                
                all_profiles.extend(profiles_batch)
                
                # If we got fewer profiles than the limit, we've reached the end
                if len(profiles_batch) < limit:
                    break
                
                offset += limit
            
            logger.info(f"Found {len(all_profiles)} total profiles")
            
            # Filter for TikTok profiles (profiles with "tiktok" in the name)
            tiktok_profiles = []
            for profile in all_profiles:
                name = profile.get('name', '').lower()
                if 'tiktok' in name:
                    tiktok_profiles.append(profile)
            
            logger.info(f"Found {len(tiktok_profiles)} TikTok profiles")
            
            return tiktok_profiles
        
        except Exception as e:
            logger.error(f"Error searching for profiles: {e}")
            return []
    
    def map_profiles_to_proxies(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map each profile to a proxy credential.
        
        Args:
            profiles: List of profile dictionaries from MultiLogin
        
        Returns:
            List of mapped profile dictionaries
        """
        logger.info("Mapping profiles to proxies...")
        
        mapped_profiles = []
        
        for i, profile in enumerate(profiles):
            # Get proxy for this profile (cycle through proxies if we have more profiles than proxies)
            proxy_index = i % len(self.proxies)
            proxy = self.proxies[proxy_index]
            
            mapped_profile = {
                'name': profile.get('name', f'TIKTOK{i+1}'),
                'uuid': profile.get('uuid'),
                'folder_id': profile.get('folder_id'),
                'proxy': {
                    'host': proxy.host,
                    'port': proxy.port,
                    'username': proxy.username,
                    'password': proxy.password,
                    'country_code': proxy.country_code
                }
            }
            
            mapped_profiles.append(mapped_profile)
            
            logger.info(f"  Mapped {mapped_profile['name']} -> {proxy.country_code} proxy")
        
        return mapped_profiles
    
    def save_profiles_to_database(self, profiles: List[Dict[str, Any]]):
        """
        Save all mapped profiles to the database.
        
        Args:
            profiles: List of mapped profile dictionaries
        """
        logger.info("Saving profiles to database...")
        
        for profile in profiles:
            try:
                # Check if profile already exists
                existing = self.database.get_profile_by_uuid(profile['uuid'])
                
                if existing:
                    logger.info(f"  Profile {profile['name']} already in database, skipping")
                    continue
                
                # Add profile to database
                self.database.add_profile(
                    name=profile['name'],
                    multilogin_uuid=profile['uuid'],
                    multilogin_folder_id=profile.get('folder_id', ''),
                    proxy_host=profile['proxy']['host'],
                    proxy_port=profile['proxy']['port'],
                    proxy_username=profile['proxy']['username'],
                    proxy_password=profile['proxy']['password'],
                    status='active'
                )
                
                self.loaded_profiles.append(profile)
                logger.info(f"  ✓ Saved {profile['name']} to database")
            
            except Exception as e:
                logger.error(f"  ✗ Failed to save {profile['name']}: {e}")
                self.failed_profiles.append({
                    'profile': profile,
                    'error': str(e)
                })
    
    def save_mapping_file(self, profiles: List[Dict[str, Any]], output_path: str):
        """
        Save the profile mapping to a JSON file for reference.
        
        Args:
            profiles: List of mapped profile dictionaries
            output_path: Path to save the JSON file
        """
        logger.info(f"Saving profile mapping to {output_path}...")
        
        try:
            mapping = {}
            for profile in profiles:
                mapping[profile['name']] = {
                    'uuid': profile['uuid'],
                    'folder_id': profile.get('folder_id', ''),
                    'proxy': profile['proxy']
                }
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(mapping, f, indent=2)
            
            logger.info(f"✓ Profile mapping saved to {output_path}")
        
        except Exception as e:
            logger.error(f"Failed to save mapping file: {e}")
    
    def run(self) -> bool:
        """
        Execute the complete profile loading workflow.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 70)
        logger.info("MULTILOGIN PROFILE LOADER - STARTING")
        logger.info("=" * 70)
        
        try:
            # Step 1: Load proxies
            self.load_proxies()
            
            if not self.proxies:
                logger.error("No proxies loaded. Cannot proceed.")
                return False
            
            # Step 2: Search for existing profiles
            existing_profiles = self.search_existing_profiles()
            
            if not existing_profiles:
                logger.error("No existing TikTok profiles found in MultiLogin account.")
                logger.error("Please create profiles manually in MultiLogin first.")
                return False
            
            # Step 3: Map profiles to proxies
            mapped_profiles = self.map_profiles_to_proxies(existing_profiles)
            
            # Step 4: Save to database
            self.save_profiles_to_database(mapped_profiles)
            
            # Step 5: Save mapping file
            mapping_file = os.path.join(
                os.path.dirname(self.config['database_path']),
                'profile_mapping.json'
            )
            self.save_mapping_file(mapped_profiles, mapping_file)
            
            # Print summary
            logger.info("=" * 70)
            logger.info("PROFILE LOADING COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Total profiles found: {len(existing_profiles)}")
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
    """Main entry point for the profile loader."""
    parser = argparse.ArgumentParser(
        description="Load existing MultiLogin profiles and map them to proxies"
    )
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to .env file (default: .env)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without actually saving to database'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv(args.env_file)
    
    # Build configuration
    config = {
        'proxy_file_path': os.getenv('PROXY_FILE_PATH', 'data/nodemaven_proxies.txt'),
        'multilogin_api_base_url': os.getenv('MULTILOGIN_API_BASE_URL', 'https://api.multilogin.com'),
        'multilogin_email': os.getenv('MULTILOGIN_EMAIL'),
        'multilogin_password': os.getenv('MULTILOGIN_PASSWORD'),
        'multilogin_automation_token': os.getenv('MULTILOGIN_AUTOMATION_TOKEN'),
        'database_path': os.getenv('DATABASE_PATH', 'data/affilify_system.db')
    }
    
    # Validate required configuration
    required_fields = ['multilogin_email', 'multilogin_password']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        logger.error(f"Missing required configuration: {', '.join(missing_fields)}")
        logger.error("Please check your .env file")
        sys.exit(1)
    
    # Create and run profile loader
    loader = ProfileLoader(config)
    success = loader.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
