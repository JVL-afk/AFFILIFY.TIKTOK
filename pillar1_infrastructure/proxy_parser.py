"""
Nodemaven Proxy Parser
=======================
This module parses the Nodemaven proxy credentials from the configuration file
and extracts all relevant information including host, port, username, password,
country code, proxy type, and session ID.

The proxy format from Nodemaven is:
host:port:username-country-XX-type-mobile-sid-XXXXX-filter-medium:password

Example:
gate.nodemaven.com:1080:TikTokmoney1-country-al-type-mobile-sid-dda50bfbeb764-filter-medium:ef5e8ff0ee354
"""

import re
from dataclasses import dataclass
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProxyCredentials:
    """
    Data class representing a single Nodemaven proxy configuration.
    
    Attributes:
        host: Proxy server hostname (e.g., "gate.nodemaven.com")
        port: Proxy server port (e.g., 1080)
        username: Full username string including all parameters
        password: Proxy password
        country_code: ISO 3166-1 alpha-2 country code (e.g., "al" for Albania)
        proxy_type: Type of proxy (e.g., "mobile", "residential")
        session_id: Unique session identifier for sticky sessions
        filter_level: Filter level (e.g., "medium", "high")
        account_name: Extracted account name from username (e.g., "TikTokmoney1")
        index: Index number of this proxy in the list (0-based)
    """
    host: str
    port: int
    username: str
    password: str
    country_code: str
    proxy_type: str
    session_id: str
    filter_level: str
    account_name: str
    index: int
    
    def to_dict(self) -> dict:
        """Convert the proxy credentials to a dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "country_code": self.country_code,
            "proxy_type": self.proxy_type,
            "session_id": self.session_id,
            "filter_level": self.filter_level,
            "account_name": self.account_name,
            "index": self.index
        }
    
    def to_socks5_url(self) -> str:
        """
        Convert to SOCKS5 URL format.
        
        Returns:
            SOCKS5 URL string (e.g., "socks5://user:pass@host:port")
        """
        return f"socks5://{self.username}:{self.password}@{self.host}:{self.port}"
    
    def to_multilogin_proxy_object(self) -> dict:
        """
        Convert to MultiLogin API proxy object format.
        
        Returns:
            Dictionary in the format expected by MultiLogin API
        """
        return {
            "host": self.host,
            "type": "socks5",
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "save_traffic": False  # Don't save traffic by default
        }


class ProxyParser:
    """
    Parser for Nodemaven proxy credentials.
    
    This class handles reading the proxy file, parsing each line,
    and extracting all relevant information.
    """
    
    # Regex pattern to extract information from the username field
    USERNAME_PATTERN = re.compile(
        r'^(?P<account_name>[^-]+)-'
        r'country-(?P<country_code>[a-z]{2})-'
        r'type-(?P<proxy_type>\w+)-'
        r'sid-(?P<session_id>[a-f0-9]+)-'
        r'filter-(?P<filter_level>\w+)$'
    )
    
    def __init__(self, proxy_file_path: str):
        """
        Initialize the proxy parser.
        
        Args:
            proxy_file_path: Path to the file containing proxy credentials
        """
        self.proxy_file_path = proxy_file_path
        self.proxies: List[ProxyCredentials] = []
    
    def parse(self) -> List[ProxyCredentials]:
        """
        Parse the proxy file and extract all credentials.
        
        Returns:
            List of ProxyCredentials objects
        
        Raises:
            FileNotFoundError: If the proxy file doesn't exist
            ValueError: If a proxy line is malformed
        """
        logger.info(f"Parsing proxy file: {self.proxy_file_path}")
        
        try:
            with open(self.proxy_file_path, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.error(f"Proxy file not found: {self.proxy_file_path}")
            raise
        
        proxy_index = 0
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            try:
                proxy = self._parse_line(line, proxy_index)
                self.proxies.append(proxy)
                proxy_index += 1
                logger.debug(f"Parsed proxy {proxy_index}: {proxy.account_name} ({proxy.country_code})")
            except ValueError as e:
                logger.error(f"Error parsing line {line_num}: {e}")
                logger.error(f"Line content: {line}")
                raise
        
        logger.info(f"Successfully parsed {len(self.proxies)} proxies")
        return self.proxies
    
    def _parse_line(self, line: str, index: int) -> ProxyCredentials:
        """
        Parse a single proxy line.
        
        Args:
            line: Single line from the proxy file
            index: Index number for this proxy
        
        Returns:
            ProxyCredentials object
        
        Raises:
            ValueError: If the line format is invalid
        """
        # Split by colon: host:port:username:password
        parts = line.split(':')
        
        if len(parts) != 4:
            raise ValueError(
                f"Invalid proxy format. Expected 4 parts (host:port:username:password), "
                f"got {len(parts)} parts"
            )
        
        host, port_str, username, password = parts
        
        # Validate and convert port
        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"Invalid port number: {port_str}")
        
        # Parse the username field to extract metadata
        match = self.USERNAME_PATTERN.match(username)
        
        if not match:
            raise ValueError(
                f"Username doesn't match expected pattern: {username}"
            )
        
        # Extract all components
        account_name = match.group('account_name')
        country_code = match.group('country_code')
        proxy_type = match.group('proxy_type')
        session_id = match.group('session_id')
        filter_level = match.group('filter_level')
        
        return ProxyCredentials(
            host=host,
            port=port,
            username=username,
            password=password,
            country_code=country_code,
            proxy_type=proxy_type,
            session_id=session_id,
            filter_level=filter_level,
            account_name=account_name,
            index=index
        )
    
    def get_proxy_by_index(self, index: int) -> Optional[ProxyCredentials]:
        """
        Get a proxy by its index.
        
        Args:
            index: Index number (0-based)
        
        Returns:
            ProxyCredentials object or None if index is out of range
        """
        if 0 <= index < len(self.proxies):
            return self.proxies[index]
        return None
    
    def get_proxy_by_account_name(self, account_name: str) -> Optional[ProxyCredentials]:
        """
        Get a proxy by its account name.
        
        Args:
            account_name: Account name (e.g., "TikTokmoney1")
        
        Returns:
            ProxyCredentials object or None if not found
        """
        for proxy in self.proxies:
            if proxy.account_name == account_name:
                return proxy
        return None
    
    def get_all_country_codes(self) -> List[str]:
        """
        Get a list of all unique country codes in the proxy list.
        
        Returns:
            List of unique country codes
        """
        return list(set(proxy.country_code for proxy in self.proxies))
    
    def get_proxies_by_country(self, country_code: str) -> List[ProxyCredentials]:
        """
        Get all proxies for a specific country.
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code
        
        Returns:
            List of ProxyCredentials objects
        """
        return [proxy for proxy in self.proxies if proxy.country_code == country_code]
    
    def validate_all_proxies(self) -> tuple[bool, List[str]]:
        """
        Validate that all proxies have been parsed correctly.
        
        Returns:
            Tuple of (all_valid: bool, errors: List[str])
        """
        errors = []
        
        # Check for duplicate account names
        account_names = [p.account_name for p in self.proxies]
        duplicates = set([name for name in account_names if account_names.count(name) > 1])
        
        if duplicates:
            errors.append(f"Duplicate account names found: {duplicates}")
        
        # Check for duplicate session IDs
        session_ids = [p.session_id for p in self.proxies]
        duplicate_sessions = set([sid for sid in session_ids if session_ids.count(sid) > 1])
        
        if duplicate_sessions:
            errors.append(f"Duplicate session IDs found: {duplicate_sessions}")
        
        # Check that all proxies have the same host and port
        hosts = set(p.host for p in self.proxies)
        ports = set(p.port for p in self.proxies)
        
        if len(hosts) > 1:
            errors.append(f"Multiple proxy hosts found: {hosts}")
        
        if len(ports) > 1:
            errors.append(f"Multiple proxy ports found: {ports}")
        
        return (len(errors) == 0, errors)


if __name__ == "__main__":
    # Test the parser
    import sys
    
    logging.basicConfig(level=logging.DEBUG)
    
    if len(sys.argv) > 1:
        proxy_file = sys.argv[1]
    else:
        proxy_file = "/home/ubuntu/affilify_tiktok_system/data/nodemaven_proxies.txt"
    
    parser = ProxyParser(proxy_file)
    proxies = parser.parse()
    
    print(f"\nParsed {len(proxies)} proxies")
    print("=" * 80)
    
    # Show first 3 proxies
    for i, proxy in enumerate(proxies[:3]):
        print(f"\nProxy {i}:")
        print(f"  Account: {proxy.account_name}")
        print(f"  Country: {proxy.country_code}")
        print(f"  Type: {proxy.proxy_type}")
        print(f"  Session ID: {proxy.session_id}")
        print(f"  SOCKS5 URL: {proxy.to_socks5_url()}")
    
    # Validate
    valid, errors = parser.validate_all_proxies()
    print(f"\nValidation: {'PASSED' if valid else 'FAILED'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    
    # Show country distribution
    countries = parser.get_all_country_codes()
    print(f"\nCountry distribution ({len(countries)} unique countries):")
    for country in sorted(countries)[:10]:
        count = len(parser.get_proxies_by_country(country))
        print(f"  {country.upper()}: {count}")
