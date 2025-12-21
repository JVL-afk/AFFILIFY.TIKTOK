#!/usr/bin/env python3
"""
Test Script: MultiLogin Profile Launch
=======================================
This script tests that the system can successfully launch and connect to
an existing MultiLogin profile using the Local Launcher API.

Usage:
    python3 test_profile_launch.py [--profile-name TIKTOK1]
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pillar1_infrastructure.multilogin_client import MultiLoginClient, MultiLoginAPIError
from shared.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(
        description="Test MultiLogin profile launching"
    )
    parser.add_argument(
        '--profile-name',
        help='Specific profile name to test (default: first profile in database)'
    )
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to .env file (default: .env)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("MULTILOGIN PROFILE LAUNCH TEST")
    print("=" * 70)
    print()
    
    # Load environment variables
    load_dotenv(args.env_file)
    
    # Check required configuration
    required_vars = ['MULTILOGIN_EMAIL', 'MULTILOGIN_PASSWORD', 'DATABASE_PATH']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print(f"   Please check your {args.env_file} file")
        sys.exit(1)
    
    # Initialize MultiLogin client
    print("Step 1: Initializing MultiLogin client...")
    try:
        client = MultiLoginClient(
            base_url=os.getenv('MULTILOGIN_API_BASE_URL', 'https://api.multilogin.com'),
            email=os.getenv('MULTILOGIN_EMAIL'),
            password=os.getenv('MULTILOGIN_PASSWORD'),
            automation_token=os.getenv('MULTILOGIN_AUTOMATION_TOKEN')
        )
        print("✅ MultiLogin client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize MultiLogin client: {e}")
        sys.exit(1)
    
    print()
    
    # Load database
    print("Step 2: Loading profile from database...")
    try:
        db = Database(os.getenv('DATABASE_PATH', 'data/affilify_system.db'))
        
        if args.profile_name:
            # Get specific profile
            test_profile = db.get_profile_by_name(args.profile_name)
            if not test_profile:
                print(f"❌ Profile '{args.profile_name}' not found in database")
                sys.exit(1)
        else:
            # Get first profile
            profiles = db.get_all_profiles()
            if not profiles:
                print("❌ No profiles found in database!")
                print("   Please run: python3 pillar1_infrastructure/profile_loader.py")
                sys.exit(1)
            test_profile = profiles[0]
        
        print(f"✅ Loaded profile: {test_profile['profile_name']}")
        print(f"   UUID: {test_profile['profile_id']}")
        print(f"   Proxy: {test_profile.get('proxy_host', 'N/A')}")
    except Exception as e:
        print(f"❌ Failed to load profile: {e}")
        sys.exit(1)
    
    print()
    
    # Test profile launch
    print("Step 3: Testing profile launch...")
    print("   (This will open the MultiLogin browser profile)")
    print()
    
    try:
        print("🚀 Starting profile...")
        connection_info = client.start_profile(
            profile_uuid=test_profile['profile_id'],
            automation_type="playwright"
        )
        
        print("✅ Profile started successfully!")
        print()
        print("Connection Details:")
        print(f"   WebSocket endpoint: {connection_info.get('ws_endpoint', 'N/A')}")
        print(f"   HTTP debug port: {connection_info.get('http_debug_port', 'N/A')}")
        print()
        
        # Wait a moment
        import time
        print("Waiting 3 seconds...")
        time.sleep(3)
        
        # Stop the profile
        print()
        print("🛑 Stopping profile...")
        success = client.stop_profile(test_profile['profile_id'])
        
        if success:
            print("✅ Profile stopped successfully!")
        else:
            print("⚠️  Profile stop returned false (may already be stopped)")
        
        print()
        print("=" * 70)
        print("✅ TEST PASSED!")
        print("=" * 70)
        print()
        print("Your MultiLogin profiles are working correctly!")
        print("You can now run the full system.")
        print()
        
    except MultiLoginAPIError as e:
        print(f"❌ MultiLogin API Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure MultiLogin application is running")
        print("  2. Check that https://launcher.mlx.yt:45001 is accessible")
        print("  3. Verify your MultiLogin credentials in .env")
        print("  4. Check that the profile UUID is correct")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
