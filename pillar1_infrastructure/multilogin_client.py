"""
MultiLogin API Client
======================
This module provides a Python client for the MultiLogin X API.
It handles authentication, profile creation, and profile management.

API Documentation: https://documenter.getpostman.com/view/28533318/2s946h9Cv9
"""

import requests
import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MultiLoginAPIError(Exception):
    """Custom exception for MultiLogin API errors."""
    pass


class MultiLoginClient:
    """
    Client for interacting with the MultiLogin X API.
    
    This client handles:
    - Authentication (bearer token)
    - Profile creation
    - Profile management
    - Error handling and retries
    """
    
    def __init__(self, base_url: str, email: str, password: str, 
                 automation_token: Optional[str] = None):
        """
        Initialize the MultiLogin API client.
        
        Args:
            base_url: Base URL for the MultiLogin API
            email: MultiLogin account email
            password: MultiLogin account password
            automation_token: Optional automation token for extended sessions
        """
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        self.automation_token = automation_token
        
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _ensure_authenticated(self):
        """
        Ensure we have a valid access token.
        
        If the token is expired or doesn't exist, authenticate.
        """
        if self.automation_token:
            # Use automation token (doesn't expire)
            self.access_token = self.automation_token
            logger.info("Using automation token for authentication")
            return
        
        # Check if we need to refresh the token
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                # Token is still valid
                return
        
        # Need to authenticate
        self._authenticate()
    
    def _authenticate(self):
        """
        Authenticate with the MultiLogin API and get an access token.
        
        Raises:
            MultiLoginAPIError: If authentication fails
        """
        logger.info("Authenticating with MultiLogin API...")
        
        url = f"{self.base_url}/user/signin"
        payload = {
            "email": self.email,
            "password": self.password
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'token' in data['data']:
                self.access_token = data['data']['token']
                # Tokens expire after 30 minutes
                self.token_expires_at = datetime.now() + timedelta(minutes=28)
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                logger.info("Successfully authenticated with MultiLogin API")
            else:
                raise MultiLoginAPIError(f"Unexpected response format: {data}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            raise MultiLoginAPIError(f"Failed to authenticate: {e}")
    
    def create_profile(self, profile_config: Dict[str, Any], 
                      strict_mode: bool = False) -> Dict[str, Any]:
        """
        Create a new MultiLogin browser profile.
        
        Args:
            profile_config: Profile configuration dictionary
            strict_mode: If True, use strict mode (all parameters required)
        
        Returns:
            Dictionary containing the created profile information
        
        Raises:
            MultiLoginAPIError: If profile creation fails
        """
        self._ensure_authenticated()
        
        url = f"{self.base_url}/profile/create"
        
        headers = {}
        if strict_mode:
            headers['X-Strict-Mode'] = 'true'
        
        logger.info(f"Creating profile: {profile_config.get('name', 'unnamed')}")
        
        try:
            response = self.session.post(
                url, 
                json=profile_config, 
                headers=headers,
                timeout=60
            )
            
            # Log the response for debugging
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                profile_data = data['data']
                logger.info(f"Successfully created profile: {profile_data.get('uuid', 'unknown')}")
                return profile_data
            else:
                raise MultiLoginAPIError(f"Unexpected response format: {data}")
        
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error creating profile: {e}"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg += f" - {error_data}"
                except:
                    error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise MultiLoginAPIError(error_msg)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error creating profile: {e}")
            raise MultiLoginAPIError(f"Failed to create profile: {e}")
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific profile.
        
        Args:
            profile_id: UUID of the profile
        
        Returns:
            Profile information dictionary or None if not found
        """
        self._ensure_authenticated()
        
        url = f"{self.base_url}/profile/{profile_id}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data')
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error getting profile: {e}")
            raise MultiLoginAPIError(f"Failed to get profile: {e}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error getting profile: {e}")
            raise MultiLoginAPIError(f"Failed to get profile: {e}")
    
    def search_profiles(self, query: Optional[str] = None, 
                       folder_id: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for profiles.
        
        Args:
            query: Optional search query
            folder_id: Optional folder ID to filter by
            limit: Maximum number of results
        
        Returns:
            List of profile dictionaries
        """
        self._ensure_authenticated()
        
        url = f"{self.base_url}/profile/search"
        
        payload = {
            "limit": limit
        }
        
        if query:
            payload["query"] = query
        
        if folder_id:
            payload["folder_id"] = folder_id
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching profiles: {e}")
            raise MultiLoginAPIError(f"Failed to search profiles: {e}")
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile.
        
        Args:
            profile_id: UUID of the profile to delete
        
        Returns:
            True if successful
        """
        self._ensure_authenticated()
        
        url = f"{self.base_url}/profile/remove"
        
        payload = {
            "ids": [profile_id]
        }
        
        try:
            response = self.session.delete(url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Successfully deleted profile: {profile_id}")
            return True
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting profile: {e}")
            raise MultiLoginAPIError(f"Failed to delete profile: {e}")
    
    def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing profile.
        
        Args:
            profile_id: UUID of the profile to update
            updates: Dictionary of fields to update
        
        Returns:
            Updated profile information
        """
        self._ensure_authenticated()
        
        url = f"{self.base_url}/profile/update"
        
        payload = {
            "uuid": profile_id,
            **updates
        }
        
        try:
            response = self.session.put(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully updated profile: {profile_id}")
            return data.get('data', {})
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating profile: {e}")
            raise MultiLoginAPIError(f"Failed to update profile: {e}")
    
    def start_profile(self, profile_uuid: str, automation_type: str = "playwright") -> Dict[str, Any]:
        """
        Start a profile using the Local Launcher API.
        
        Args:
            profile_uuid: UUID of the profile to start
            automation_type: Type of automation ("playwright" or "selenium")
        
        Returns:
            Dictionary containing connection information (ws_endpoint, http_debug_port, etc.)
        
        Raises:
            MultiLoginAPIError: If profile start fails
        """
        # Local Launcher API uses a different base URL
        launcher_url = "https://launcher.mlx.yt:45001/api/v1/profile/start"
        
        params = {
            "automation_type": automation_type,
            "profile_id": profile_uuid
        }
        
        logger.info(f"Starting profile {profile_uuid} with {automation_type}...")
        
        try:
            response = requests.get(
                launcher_url,
                params=params,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                connection_info = data.get('data', {})
                logger.info(f"Successfully started profile: {profile_uuid}")
                logger.debug(f"Connection info: {connection_info}")
                return connection_info
            else:
                error_msg = data.get('message', 'Unknown error')
                raise MultiLoginAPIError(f"Failed to start profile: {error_msg}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error starting profile: {e}")
            raise MultiLoginAPIError(f"Failed to start profile: {e}")
    
    def stop_profile(self, profile_uuid: str) -> bool:
        """
        Stop a running profile using the Local Launcher API.
        
        Args:
            profile_uuid: UUID of the profile to stop
        
        Returns:
            True if successful
        
        Raises:
            MultiLoginAPIError: If profile stop fails
        """
        launcher_url = "https://launcher.mlx.yt:45001/api/v1/profile/stop"
        
        params = {
            "profile_id": profile_uuid
        }
        
        logger.info(f"Stopping profile {profile_uuid}...")
        
        try:
            response = requests.get(
                launcher_url,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                logger.info(f"Successfully stopped profile: {profile_uuid}")
                return True
            else:
                error_msg = data.get('message', 'Unknown error')
                logger.warning(f"Failed to stop profile: {error_msg}")
                return False
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error stopping profile: {e}")
            return False
    
    def get_active_profile_ports(self, profile_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get the active ports for a running profile.
        
        Args:
            profile_uuid: UUID of the profile
        
        Returns:
            Dictionary containing port information or None if profile is not running
        """
        launcher_url = "https://launcher.mlx.yt:45001/api/v1/profile/active"
        
        params = {
            "profile_id": profile_uuid
        }
        
        try:
            response = requests.get(
                launcher_url,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                return data.get('data')
            else:
                return None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting active profile ports: {e}")
            return None
    
    def create_profile_with_retry(self, profile_config: Dict[str, Any],
                                 max_retries: int = 3,
                                 retry_delay: int = 5) -> Dict[str, Any]:
        """
        Create a profile with automatic retry on failure.
        
        Args:
            profile_config: Profile configuration dictionary
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        
        Returns:
            Created profile information
        
        Raises:
            MultiLoginAPIError: If all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return self.create_profile(profile_config)
            except MultiLoginAPIError as e:
                last_error = e
                logger.warning(f"Profile creation attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        
        # All retries failed
        raise MultiLoginAPIError(
            f"Failed to create profile after {max_retries} attempts. "
            f"Last error: {last_error}"
        )


def build_profile_config(name: str, folder_id: str, proxy_config: Dict[str, Any],
                        timezone: str, browser_type: str = "mimic",
                        os_type: str = "windows") -> Dict[str, Any]:
    """
    Build a complete profile configuration for the MultiLogin API.
    
    This function creates a profile configuration with all the necessary
    parameters for maximum stealth and anti-detection.
    
    Args:
        name: Profile name
        folder_id: Folder ID where the profile will be created
        proxy_config: Proxy configuration dictionary
        timezone: IANA timezone identifier (e.g., "America/New_York")
        browser_type: "mimic" or "stealthfox"
        os_type: "windows", "macos", "linux", or "android"
    
    Returns:
        Complete profile configuration dictionary
    """
    config = {
        "name": name,
        "browser_type": browser_type,
        "folder_id": folder_id,
        "os_type": os_type,
        "auto_update_core": True,  # Keep browser core up-to-date
        "parameters": {
            "flags": {
                # Required flags
                "webrtc_masking": "mask",
                "proxy_masking": "custom",  # We're using a proxy
                "geolocation_popup": "allow",  # Allow geolocation
                "audio_masking": "natural",
                "graphics_noise": "mask",
                "ports_masking": "mask",
                "navigator_masking": "mask",
                "localization_masking": "mask",
                "timezone_masking": "mask",
                "graphics_masking": "mask",
                "fonts_masking": "mask",
                "media_devices_masking": "natural",
                "screen_masking": "mask",
                "geolocation_masking": "mask",
                "canvas_noise": "mask",
                "startup_behavior": "recover"  # Restore previous session
            },
            "fingerprint": {
                "timezone": {
                    "fill_based_on_ip": False,
                    "value": timezone  # Set to match proxy location
                }
            },
            "storage": {
                "is_local": True,  # Store locally for better performance
                "save_service_worker": True
            },
            "proxy": proxy_config,
            "custom_start_urls": []
        }
    }
    
    return config


if __name__ == "__main__":
    # Test the MultiLogin client
    import os
    from dotenv import load_dotenv
    
    logging.basicConfig(level=logging.DEBUG)
    
    # Load environment variables
    load_dotenv("/home/ubuntu/affilify_tiktok_system/.env")
    
    base_url = os.getenv("MULTILOGIN_API_BASE_URL", "https://api.multilogin.com")
    email = os.getenv("MULTILOGIN_EMAIL", "")
    password = os.getenv("MULTILOGIN_PASSWORD", "")
    
    if not email or not password:
        print("ERROR: Please set MULTILOGIN_EMAIL and MULTILOGIN_PASSWORD in .env file")
        exit(1)
    
    client = MultiLoginClient(base_url, email, password)
    
    print("Testing MultiLogin API Client...")
    print("=" * 80)
    
    # Test authentication
    try:
        client._authenticate()
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        exit(1)
    
    # Test searching profiles
    try:
        profiles = client.search_profiles(limit=5)
        print(f"✅ Found {len(profiles)} existing profiles")
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    print("\nMultiLogin API client test completed!")
