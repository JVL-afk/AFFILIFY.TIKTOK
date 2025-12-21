#!/usr/bin/env python3
"""
Profile UUID Extraction Script
===============================
This script connects to the MultiLogin API and extracts the UUIDs of all existing profiles.
It creates a mapping file that the main system will use instead of creating new profiles.

Usage:
    python3 extract_profile_uuids.py

Requirements:
    - MULTILOGIN_API_TOKEN must be set in .env file
    - Internet connection to reach api.multilogin.com
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from shared.database import Database

class ProfileExtractor:
    """Extracts profile UUIDs from MultiLogin account"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.multilogin.com"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def search_profiles(self, offset: int = 0, limit: int = 100, 
                       search_text: str = "", storage_type: str = "cloud") -> Dict:
        """
        Search for profiles using the Profile Search API
        
        Args:
            offset: Pagination offset
            limit: Number of profiles to return (max 100)
            search_text: Optional search filter
            storage_type: "cloud" or "local"
            
        Returns:
            API response containing profile list
        """
        url = f"{self.base_url}/profile/search"
        
        payload = {
            "offset": offset,
            "limit": limit,
            "search_text": search_text,
            "storage_type": storage_type
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching profiles: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def get_all_profiles(self) -> List[Dict]:
        """
        Get all profiles from the account (handles pagination)
        
        Returns:
            List of all profile dictionaries
        """
        all_profiles = []
        offset = 0
        limit = 100
        
        print("🔍 Searching for profiles...")
        
        while True:
            result = self.search_profiles(offset=offset, limit=limit)
            
            if not result or 'data' not in result:
                break
            
            profiles = result['data'].get('profiles', [])
            
            if not profiles:
                break
            
            all_profiles.extend(profiles)
            print(f"   Found {len(profiles)} profiles (total: {len(all_profiles)})")
            
            # Check if there are more profiles
            if len(profiles) < limit:
                break
            
            offset += limit
        
        return all_profiles
    
    def filter_tiktok_profiles(self, profiles: List[Dict]) -> List[Dict]:
        """
        Filter profiles to only include TikTok profiles
        
        Args:
            profiles: List of all profiles
            
        Returns:
            List of TikTok profiles only
        """
        tiktok_profiles = []
        
        for profile in profiles:
            name = profile.get('name', '').upper()
            if 'TIKTOK' in name:
                tiktok_profiles.append(profile)
        
        return tiktok_profiles
    
    def create_profile_mapping(self, profiles: List[Dict], 
                              proxy_data_path: str) -> Dict:
        """
        Create a mapping of profile names to UUIDs and proxy credentials
        
        Args:
            profiles: List of profile dictionaries
            proxy_data_path: Path to the proxy data file
            
        Returns:
            Dictionary mapping profile names to their data
        """
        # Load proxy data
        proxy_credentials = self._load_proxy_data(proxy_data_path)
        
        mapping = {}
        
        for i, profile in enumerate(profiles):
            profile_name = profile.get('name', f'TIKTOK{i+1}')
            profile_uuid = profile.get('uuid')
            folder_id = profile.get('folder_id')
            
            if not profile_uuid:
                print(f"⚠️  Warning: Profile '{profile_name}' has no UUID, skipping")
                continue
            
            # Try to match with proxy data
            proxy_creds = None
            if i < len(proxy_credentials):
                proxy_creds = proxy_credentials[i]
            
            mapping[profile_name] = {
                "uuid": profile_uuid,
                "folder_id": folder_id,
                "name": profile_name,
                "proxy": proxy_creds
            }
        
        return mapping
    
    def _load_proxy_data(self, proxy_data_path: str) -> List[Dict]:
        """Load proxy credentials from file"""
        try:
            with open(proxy_data_path, 'r') as f:
                lines = f.readlines()
            
            proxy_list = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse proxy string
                # Format: gate.nodemaven.com:1080:session_id:password
                parts = line.split(':')
                if len(parts) >= 4:
                    proxy_list.append({
                        "host": parts[0],
                        "port": parts[1],
                        "username": parts[2],
                        "password": ':'.join(parts[3:])  # In case password contains ':'
                    })
            
            return proxy_list
        except Exception as e:
            print(f"⚠️  Warning: Could not load proxy data: {e}")
            return []
    
    def save_mapping(self, mapping: Dict, output_path: str):
        """Save the profile mapping to a JSON file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(mapping, f, indent=2)
            print(f"✅ Profile mapping saved to: {output_path}")
        except Exception as e:
            print(f"❌ Error saving mapping: {e}")
    
    def save_to_database(self, mapping: Dict, db_path: str):
        """Save the profile mapping to the database"""
        try:
            db = Database(db_path)
            
            for profile_name, data in mapping.items():
                # Check if profile already exists
                existing = db.get_profile_by_name(profile_name)
                
                if existing:
                    print(f"   Profile '{profile_name}' already in database, skipping")
                    continue
                
                # Add profile to database
                proxy = data.get('proxy', {})
                db.add_profile(
                    name=profile_name,
                    multilogin_uuid=data['uuid'],
                    multilogin_folder_id=data['folder_id'],
                    proxy_host=proxy.get('host', ''),
                    proxy_port=proxy.get('port', ''),
                    proxy_username=proxy.get('username', ''),
                    proxy_password=proxy.get('password', ''),
                    status='active'
                )
            
            print(f"✅ Profile mapping saved to database: {db_path}")
        except Exception as e:
            print(f"❌ Error saving to database: {e}")


def main():
    """Main execution function"""
    print("=" * 70)
    print("MultiLogin Profile UUID Extraction Script")
    print("=" * 70)
    print()
    
    # Load environment variables
    load_dotenv()
    
    api_token = os.getenv('MULTILOGIN_API_TOKEN')
    if not api_token:
        print("❌ Error: MULTILOGIN_API_TOKEN not found in .env file")
        print("   Please add your MultiLogin API token to the .env file")
        sys.exit(1)
    
    # Initialize extractor
    extractor = ProfileExtractor(api_token)
    
    # Get all profiles
    print("Step 1: Fetching all profiles from MultiLogin account...")
    all_profiles = extractor.get_all_profiles()
    
    if not all_profiles:
        print("❌ No profiles found or error occurred")
        sys.exit(1)
    
    print(f"✅ Found {len(all_profiles)} total profiles")
    print()
    
    # Filter TikTok profiles
    print("Step 2: Filtering TikTok profiles...")
    tiktok_profiles = extractor.filter_tiktok_profiles(all_profiles)
    print(f"✅ Found {len(tiktok_profiles)} TikTok profiles")
    print()
    
    # Display profile names
    print("TikTok Profiles:")
    for i, profile in enumerate(tiktok_profiles, 1):
        print(f"   {i}. {profile.get('name')}")
    print()
    
    # Create mapping
    print("Step 3: Creating profile mapping...")
    proxy_data_path = "data/proxies.txt"
    mapping = extractor.create_profile_mapping(tiktok_profiles, proxy_data_path)
    print(f"✅ Created mapping for {len(mapping)} profiles")
    print()
    
    # Save mapping
    print("Step 4: Saving profile mapping...")
    output_path = "data/profile_mapping.json"
    extractor.save_mapping(mapping, output_path)
    
    # Save to database
    db_path = "data/affilify_system.db"
    extractor.save_to_database(mapping, db_path)
    print()
    
    # Summary
    print("=" * 70)
    print("✅ EXTRACTION COMPLETE!")
    print("=" * 70)
    print(f"Total profiles extracted: {len(mapping)}")
    print(f"Mapping file: {output_path}")
    print(f"Database: {db_path}")
    print()
    print("You can now use the main system with your existing profiles!")
    print("=" * 70)


if __name__ == "__main__":
    main()
