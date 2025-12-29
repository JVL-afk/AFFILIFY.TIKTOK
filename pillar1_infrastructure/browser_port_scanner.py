"""
Browser Port Scanner

This module scans for running Chrome/Chromium browsers on local ports
and retrieves their Chrome DevTools Protocol (CDP) endpoints.

This is used as a fallback when MultiLogin Local Launcher API is not available.
"""

import socket
import requests
import logging
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)


class BrowserPortScanner:
    """Scans for running browsers on local ports and retrieves CDP endpoints."""
    
    # Common port ranges for Chrome DevTools Protocol
    DEFAULT_PORT_RANGE = (1080, 1080)
    
    def __init__(self, port_range: tuple = None):
        """
        Initialize the browser port scanner.
        
        Args:
            port_range: Tuple of (start_port, end_port) to scan. Defaults to (1080, 1080).
        """
        self.port_range = port_range or self.DEFAULT_PORT_RANGE
        logger.info(f"Initialized BrowserPortScanner with port range {self.port_range}")
    
    def is_port_open(self, port: int, timeout: float = 0.5) -> bool:
        """
        Check if a port is open on localhost.
        
        Args:
            port: Port number to check
            timeout: Connection timeout in seconds
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Error checking port {port}: {e}")
            return False
    
    def get_browser_info(self, port: int) -> Optional[Dict]:
        """
        Get browser information from a CDP endpoint.
        
        Args:
            port: Port number to query
            
        Returns:
            Dictionary with browser info, or None if not a browser
        """
        try:
            # Try to get version info from CDP endpoint
            response = requests.get(
                f"http://127.0.0.1:{port}/json/version",
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Found browser on port {port}: {data.get('Browser', 'Unknown')}")
                return {
                    'port': port,
                    'browser': data.get('Browser', 'Unknown'),
                    'protocol_version': data.get('Protocol-Version', 'Unknown'),
                    'user_agent': data.get('User-Agent', 'Unknown'),
                    'ws_endpoint': data.get('webSocketDebuggerUrl', ''),
                    'cdp_url': f"http://127.0.0.1:{port}"
                }
        except Exception as e:
            logger.debug(f"Port {port} is not a browser CDP endpoint: {e}")
        
        return None
    
    def get_browser_targets(self, port: int) -> List[Dict]:
        """
        Get all targets (tabs/pages) from a browser.
        
        Args:
            port: Port number to query
            
        Returns:
            List of target dictionaries
        """
        try:
            response = requests.get(
                f"http://127.0.0.1:{port}/json/list",
                timeout=2
            )
            
            if response.status_code == 200:
                targets = response.json()
                logger.debug(f"Found {len(targets)} targets on port {port}")
                return targets
        except Exception as e:
            logger.debug(f"Error getting targets from port {port}: {e}")
        
        return []
    
    def scan_for_browsers(self) -> List[Dict]:
        """
        Scan the configured port range for running browsers.
        
        Returns:
            List of dictionaries containing browser information
        """
        logger.info(f"Scanning ports {self.port_range[0]}-{self.port_range[1]} for browsers...")
        
        browsers = []
        start_port, end_port = self.port_range
        
        for port in range(start_port, end_port + 1):
            if self.is_port_open(port):
                logger.debug(f"Port {port} is open, checking if it's a browser...")
                browser_info = self.get_browser_info(port)
                
                if browser_info:
                    # Get targets for this browser
                    targets = self.get_browser_targets(port)
                    browser_info['targets'] = targets
                    browser_info['target_count'] = len(targets)
                    
                    browsers.append(browser_info)
                    logger.info(f"✅ Found browser on port {port} with {len(targets)} targets")
        
        logger.info(f"Scan complete. Found {len(browsers)} running browsers.")
        return browsers
    
    def find_available_browser(self) -> Optional[Dict]:
        """
        Find the first available browser.
        
        Returns:
            Browser info dictionary, or None if no browser found
        """
        browsers = self.scan_for_browsers()
        
        if browsers:
            return browsers[0]
        
        logger.warning("No running browsers found!")
        return None
    
    def get_cdp_endpoint_for_profile(self, profile_index: int = 0) -> Optional[str]:
        """
        Get the CDP WebSocket endpoint for a specific profile.
        
        Args:
            profile_index: Index of the browser profile (0-based)
            
        Returns:
            WebSocket endpoint URL, or None if not found
        """
        browsers = self.scan_for_browsers()
        
        if profile_index < len(browsers):
            browser = browsers[profile_index]
            
            # Try to get the WebSocket endpoint
            if browser.get('ws_endpoint'):
                return browser['ws_endpoint']
            
            # If no ws_endpoint, construct it from the first target
            if browser.get('targets'):
                first_target = browser['targets'][0]
                if 'webSocketDebuggerUrl' in first_target:
                    return first_target['webSocketDebuggerUrl']
            
            # Fallback: construct endpoint from port
            port = browser['port']
            return f"ws://127.0.0.1:{port}/devtools/browser"
        
        logger.error(f"Profile index {profile_index} not found. Only {len(browsers)} browsers running.")
        return None


def main():
    """Test the browser port scanner."""
    logging.basicConfig(level=logging.INFO)
    
    scanner = BrowserPortScanner()
    browsers = scanner.scan_for_browsers()
    
    print(f"\n{'='*60}")
    print(f"BROWSER PORT SCAN RESULTS")
    print(f"{'='*60}\n")
    
    if browsers:
        for i, browser in enumerate(browsers):
            print(f"Browser #{i+1}:")
            print(f"  Port: {browser['port']}")
            print(f"  Browser: {browser['browser']}")
            print(f"  Targets: {browser['target_count']}")
            print(f"  CDP URL: {browser['cdp_url']}")
            print(f"  WS Endpoint: {browser.get('ws_endpoint', 'N/A')}")
            print()
    else:
        print("❌ No running browsers found!")
        print("\nMake sure you have:")
        print("1. MultiLogin X app running")
        print("2. At least one profile started")
        print("3. Profiles are using Chrome/Chromium browsers")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
