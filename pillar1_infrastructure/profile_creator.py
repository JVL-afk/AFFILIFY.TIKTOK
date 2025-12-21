"""
MultiLogin Profile Creator
===========================
This is the main script for Pillar 1 that orchestrates the creation of all
MultiLogin browser profiles with proper proxy and timezone configuration.

This script:
1. Parses all Nodemaven proxy credentials
2. Maps each proxy's country to the correct timezone
3. Creates a MultiLogin profile for each proxy
4. Stores all profile information in the database
5. Validates the setup

This ensures perfect IP/timezone matching for maximum stealth.
"""

import os
import sys
import logging
import argparse
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pillar1_infrastructure.proxy_parser import ProxyParser, ProxyCredentials
from pillar1_infrastructure.multilogin_client import MultiLoginClient, build_profile_config
from shared.country_timezone_mapper import get_timezone_for_country, validate_country_code
from shared.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProfileCreator:
    """
    Orchestrates the creation of all MultiLogin profiles.
    
    This class handles the complete workflow of:
    1. Loading proxy credentials
    2. Mapping timezones
    3. Creating profiles via MultiLogin API
    4. Storing results in database
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the profile creator.
        
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
        self.created_profiles: List[Dict[str, Any]] = []
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
        
        # Validate that all country codes have timezone mappings
        missing_timezones = []
        for proxy in self.proxies:
            if not validate_country_code(proxy.country_code):
                missing_timezones.append(proxy.country_code)
        
        if missing_timezones:
            unique_missing = list(set(missing_timezones))
            logger.error(
                f"The following country codes are missing timezone mappings: "
                f"{unique_missing}"
            )
            logger.error(
                "Please add these countries to shared/country_timezone_mapper.py"
            )
            raise ValueError(f"Missing timezone mappings for: {unique_missing}")
    
    def create_all_profiles(self, start_index: int = 0, end_index: Optional[int] = None):
        """
        Create MultiLogin profiles for all proxies.
        
        Args:
            start_index: Index to start from (0-based)
            end_index: Index to end at (exclusive), or None for all
        """
        if end_index is None:
            end_index = len(self.proxies)
        
        total_to_create = end_index - start_index
        logger.info(f"Creating {total_to_create} MultiLogin profiles...")
        
        for i in range(start_index, end_index):
            proxy = self.proxies[i]
            
            logger.info(f"Creating profile {i + 1}/{end_index} for {proxy.account_name} ({proxy.country_code.upper()})...")
            
            try:
                profile_data = self._create_single_profile(proxy)
                self.created_profiles.append(profile_data)
                logger.info(f"✅ Successfully created profile for {proxy.account_name}")
            
            except Exception as e:
                logger.error(f"❌ Failed to create profile for {proxy.account_name}: {e}")
                self.failed_profiles.append({
                    'proxy_index': proxy.index,
                    'account_name': proxy.account_name,
                    'error': str(e)
                })
        
        # Summary
        logger.info("=" * 80)
        logger.info(f"Profile creation complete!")
        logger.info(f"  ✅ Successfully created: {len(self.created_profiles)}")
        logger.info(f"  ❌ Failed: {len(self.failed_profiles)}")
        
        if self.failed_profiles:
            logger.warning("Failed profiles:")
            for failed in self.failed_profiles:
                logger.warning(f"  - {failed['account_name']}: {failed['error']}")
    
    def _create_single_profile(self, proxy: ProxyCredentials) -> Dict[str, Any]:
        """
        Create a single MultiLogin profile for a proxy.
        
        Args:
            proxy: ProxyCredentials object
        
        Returns:
            Dictionary containing the created profile information
        """
        # Get the timezone for this proxy's country
        timezone = get_timezone_for_country(proxy.country_code)
        
        # Build the profile name
        profile_name = f"Affilify_TikTok_{proxy.account_name}_{proxy.country_code.upper()}"
        
        # Build the proxy configuration for MultiLogin
        proxy_config = proxy.to_multilogin_proxy_object()
        
        # Build the complete profile configuration
        profile_config = build_profile_config(
            name=profile_name,
            folder_id=self.config['multilogin_folder_id'],
            proxy_config=proxy_config,
            timezone=timezone,
            browser_type=self.config.get('browser_type', 'mimic'),
            os_type=self.config.get('os_type', 'windows')
        )
        
        # Create the profile via API (with retry)
        api_response = self.multilogin_client.create_profile_with_retry(
            profile_config,
            max_retries=self.config.get('max_retries', 3),
            retry_delay=self.config.get('retry_delay', 5)
        )
        
        # Extract the profile ID from the response
        profile_id = api_response.get('uuid') or api_response.get('id')
        
        if not profile_id:
            raise ValueError(f"No profile ID in API response: {api_response}")
        
        # Store in database
        profile_db_data = {
            'profile_id': profile_id,
            'profile_name': profile_name,
            'proxy_index': proxy.index,
            'country_code': proxy.country_code,
            'timezone': timezone,
            'browser_type': self.config.get('browser_type', 'mimic'),
            'os_type': self.config.get('os_type', 'windows'),
            'notes': f"Created for {proxy.account_name}"
        }
        
        self.database.insert_multilogin_profile(profile_db_data)
        
        # Store proxy assignment
        proxy_db_data = {
            'proxy_index': proxy.index,
            'account_name': proxy.account_name,
            'country_code': proxy.country_code,
            'host': proxy.host,
            'port': proxy.port,
            'username': proxy.username,
            'password': proxy.password,
            'proxy_type': proxy.proxy_type,
            'session_id': proxy.session_id,
            'assigned_to_profile_id': profile_id,
            'status': 'assigned'
        }
        
        self.database.insert_proxy_assignment(proxy_db_data)
        
        # Log success to database
        self.database.log_system_event(
            level='INFO',
            component='pillar1_profile_creator',
            message=f"Created profile {profile_name} with ID {profile_id}"
        )
        
        return {
            'profile_id': profile_id,
            'profile_name': profile_name,
            'proxy_index': proxy.index,
            'country_code': proxy.country_code,
            'timezone': timezone
        }
    
    def verify_profiles(self) -> bool:
        """
        Verify that all created profiles exist in the database.
        
        Returns:
            True if verification passes
        """
        logger.info("Verifying created profiles...")
        
        db_profiles = self.database.get_all_profiles()
        
        logger.info(f"Found {len(db_profiles)} profiles in database")
        
        # Check that we have the expected number
        expected_count = len(self.created_profiles)
        actual_count = len(db_profiles)
        
        if actual_count == expected_count:
            logger.info(f"✅ Verification passed: {actual_count} profiles")
            return True
        else:
            logger.error(
                f"❌ Verification failed: Expected {expected_count}, "
                f"found {actual_count}"
            )
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the profile creation process.
        
        Returns:
            Dictionary containing summary statistics
        """
        stats = self.database.get_statistics()
        
        return {
            'total_proxies': len(self.proxies),
            'profiles_created': len(self.created_profiles),
            'profiles_failed': len(self.failed_profiles),
            'db_total_profiles': stats['total_profiles'],
            'db_active_profiles': stats['active_profiles'],
            'unique_countries': len(self.proxy_parser.get_all_country_codes())
        }


def load_config_from_env() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    # Load .env file
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '.env'
    )
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
    else:
        logger.warning(f".env file not found at {env_path}")
    
    # Build configuration
    config = {
        'proxy_file_path': os.getenv(
            'PROXY_FILE_PATH',
            '/home/ubuntu/affilify_tiktok_system/data/nodemaven_proxies.txt'
        ),
        'database_path': os.getenv(
            'DATABASE_PATH',
            '/home/ubuntu/affilify_tiktok_system/data/affilify_system.db'
        ),
        'multilogin_api_base_url': os.getenv(
            'MULTILOGIN_API_BASE_URL',
            'https://api.multilogin.com'
        ),
        'multilogin_email': os.getenv('MULTILOGIN_EMAIL', ''),
        'multilogin_password': os.getenv('MULTILOGIN_PASSWORD', ''),
        'multilogin_automation_token': os.getenv('MULTILOGIN_AUTOMATION_TOKEN', ''),
        'multilogin_folder_id': os.getenv('MULTILOGIN_FOLDER_ID', ''),
        'browser_type': os.getenv('BROWSER_TYPE', 'mimic'),
        'os_type': os.getenv('OS_TYPE', 'windows'),
        'max_retries': int(os.getenv('MAX_RETRY_ATTEMPTS', '3')),
        'retry_delay': int(os.getenv('RETRY_DELAY_SECONDS', '5'))
    }
    
    # Validate required fields
    required_fields = [
        'multilogin_email',
        'multilogin_password',
        'multilogin_folder_id'
    ]
    
    missing_fields = [f for f in required_fields if not config[f]]
    
    if missing_fields:
        raise ValueError(
            f"Missing required environment variables: {missing_fields}. "
            f"Please set them in the .env file."
        )
    
    return config


def main():
    """Main entry point for the profile creator."""
    parser = argparse.ArgumentParser(
        description='Create MultiLogin profiles for all Nodemaven proxies'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=0,
        help='Start index (0-based)'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=None,
        help='End index (exclusive), or omit for all'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse proxies and validate, but don\'t create profiles'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config_from_env()
        
        # Create the profile creator
        creator = ProfileCreator(config)
        
        # Load proxies
        creator.load_proxies()
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No profiles will be created")
            logger.info(f"Would create {len(creator.proxies)} profiles")
            return
        
        # Create profiles
        creator.create_all_profiles(
            start_index=args.start,
            end_index=args.end
        )
        
        # Verify
        creator.verify_profiles()
        
        # Print summary
        summary = creator.get_summary()
        logger.info("=" * 80)
        logger.info("FINAL SUMMARY:")
        logger.info(f"  Total proxies: {summary['total_proxies']}")
        logger.info(f"  Profiles created: {summary['profiles_created']}")
        logger.info(f"  Profiles failed: {summary['profiles_failed']}")
        logger.info(f"  Unique countries: {summary['unique_countries']}")
        logger.info(f"  Database total: {summary['db_total_profiles']}")
        logger.info(f"  Database active: {summary['db_active_profiles']}")
        logger.info("=" * 80)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
