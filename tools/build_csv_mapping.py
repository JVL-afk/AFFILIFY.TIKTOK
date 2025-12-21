#!/usr/bin/env python3
"""
CSV Mapping Builder
===================
This tool helps you create the profile_mapping.csv file by combining:
1. Your Nodemaven proxy list
2. Profile names (TIKTOK1, TIKTOK2, etc.)
3. Placeholder UUIDs (which you'll replace with real ones)

Usage:
    python3 build_csv_mapping.py --proxies data/nodemaven_proxies.txt --output data/profile_mapping.csv --count 60
"""

import argparse
import csv
import sys
from pathlib import Path


def parse_proxy_line(line: str) -> dict:
    """
    Parse a proxy line in Nodemaven format.
    
    Format: host:port:username:password
    
    Args:
        line: Proxy line string
    
    Returns:
        Dictionary with proxy details
    """
    parts = line.strip().split(':')
    
    if len(parts) < 4:
        return None
    
    return {
        'host': parts[0],
        'port': parts[1],
        'username': parts[2],
        'password': ':'.join(parts[3:])  # In case password contains ':'
    }


def load_proxies(proxy_file: str) -> list:
    """
    Load proxy credentials from file.
    
    Args:
        proxy_file: Path to proxy file
    
    Returns:
        List of proxy dictionaries
    """
    proxies = []
    
    try:
        with open(proxy_file, 'r') as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                proxy = parse_proxy_line(line)
                
                if proxy:
                    proxies.append(proxy)
                else:
                    print(f"Warning: Could not parse line {line_num}: {line}")
        
        return proxies
    
    except FileNotFoundError:
        print(f"Error: Proxy file not found: {proxy_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading proxy file: {e}")
        sys.exit(1)


def generate_csv(proxies: list, output_file: str, profile_count: int):
    """
    Generate the CSV mapping file.
    
    Args:
        proxies: List of proxy dictionaries
        output_file: Path to output CSV file
        profile_count: Number of profiles to generate
    """
    # Ensure we have enough proxies
    if len(proxies) < profile_count:
        print(f"Warning: Only {len(proxies)} proxies available for {profile_count} profiles")
        print(f"         Some proxies will be reused")
    
    # Create output directory if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Write CSV
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'profile_name',
                'profile_uuid',
                'proxy_host',
                'proxy_port',
                'proxy_username',
                'proxy_password',
                'multilogin_account',
                'notes'
            ])
            
            # Write profile rows
            for i in range(profile_count):
                profile_name = f"TIKTOK{i+1}"
                
                # Get proxy (cycle through if we run out)
                proxy = proxies[i % len(proxies)]
                
                # Generate placeholder UUID
                placeholder_uuid = f"REPLACE_WITH_UUID_{i+1}"
                
                # Write row
                writer.writerow([
                    profile_name,
                    placeholder_uuid,
                    proxy['host'],
                    proxy['port'],
                    proxy['username'],
                    proxy['password'],
                    '',  # multilogin_account (leave empty for user to fill)
                    f'Proxy {i+1}'
                ])
        
        print(f"✅ CSV file created: {output_file}")
        print(f"   Generated {profile_count} profile entries")
        print()
        print("Next steps:")
        print("1. Open the CSV file in a spreadsheet editor")
        print("2. Replace each 'REPLACE_WITH_UUID_X' with the actual profile UUID from MultiLogin")
        print("3. (Optional) Fill in the 'multilogin_account' column with which account owns each profile")
        print("4. Save the file")
        print(f"5. Run: python3 pillar1_infrastructure/manual_profile_loader.py --csv {output_file}")
    
    except Exception as e:
        print(f"Error writing CSV file: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build a profile mapping CSV file from proxy list"
    )
    parser.add_argument(
        '--proxies',
        default='data/nodemaven_proxies.txt',
        help='Path to proxy file (default: data/nodemaven_proxies.txt)'
    )
    parser.add_argument(
        '--output',
        default='data/profile_mapping.csv',
        help='Path to output CSV file (default: data/profile_mapping.csv)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=60,
        help='Number of profiles to generate (default: 60)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("CSV MAPPING BUILDER")
    print("=" * 70)
    print()
    
    # Load proxies
    print(f"Loading proxies from: {args.proxies}")
    proxies = load_proxies(args.proxies)
    print(f"✅ Loaded {len(proxies)} proxies")
    print()
    
    # Generate CSV
    print(f"Generating CSV with {args.count} profiles...")
    generate_csv(proxies, args.output, args.count)


if __name__ == '__main__':
    main()
