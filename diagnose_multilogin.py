#!/usr/bin/env python3
"""
MultiLogin Launcher Diagnostic Script
This script checks the status of MultiLogin X launcher and API
"""

import os
import sys
import subprocess
import requests
import urllib3
from pathlib import Path

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_multilogin_processes():
    """Check if MultiLogin processes are running"""
    print_header("CHECKING MULTILOGIN PROCESSES")
    
    try:
        # Get all running processes
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq multilogin*'],
            capture_output=True,
            text=True
        )
        
        if "multilogin" in result.stdout.lower():
            print_success("MultiLogin processes found:")
            print(result.stdout)
        else:
            print_error("No MultiLogin processes found!")
            
    except Exception as e:
        print_error(f"Error checking processes: {e}")

def check_launcher_process():
    """Check if launcher process is running"""
    print_header("CHECKING LAUNCHER PROCESS")
    
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq launcher*'],
            capture_output=True,
            text=True
        )
        
        if "launcher" in result.stdout.lower():
            print_success("Launcher process found:")
            print(result.stdout)
        else:
            print_error("Launcher process NOT found!")
            
    except Exception as e:
        print_error(f"Error checking launcher: {e}")

def check_ports():
    """Check if ports 45000-45010 are in use"""
    print_header("CHECKING PORTS 45000-45010")
    
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True
        )
        
        found_ports = []
        for line in result.stdout.split('\n'):
            for port in range(45000, 45011):
                if f":{port}" in line:
                    found_ports.append((port, line.strip()))
        
        if found_ports:
            print_success(f"Found {len(found_ports)} ports in use:")
            for port, line in found_ports:
                print(f"  Port {port}: {line}")
        else:
            print_error("No ports 45000-45010 are in use!")
            print_info("This means the launcher API is NOT running")
            
    except Exception as e:
        print_error(f"Error checking ports: {e}")

def test_api_endpoints():
    """Test various API endpoints"""
    print_header("TESTING API ENDPOINTS")
    
    endpoints = [
        "https://launcher.mlx.yt:45001/api/v1/version",
        "https://launcher.mlx.yt:45000/api/v1/version",
        "https://localhost:45001/api/v1/version",
        "http://localhost:45001/api/v1/version",
        "http://127.0.0.1:45001/api/v1/version",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, verify=False, timeout=2)
            print_success(f"{endpoint} - Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
        except requests.exceptions.ConnectionError:
            print_error(f"{endpoint} - Connection refused")
        except requests.exceptions.Timeout:
            print_error(f"{endpoint} - Timeout")
        except Exception as e:
            print_error(f"{endpoint} - Error: {e}")

def check_mlx_folder():
    """Check MultiLogin X folder structure"""
    print_header("CHECKING MLX FOLDER STRUCTURE")
    
    username = os.getenv('USERNAME')
    mlx_path = Path(f"C:/Users/{username}/mlx")
    
    if not mlx_path.exists():
        print_error(f"MLX folder not found at {mlx_path}")
        return
    
    print_success(f"MLX folder found at {mlx_path}")
    
    # Check important subfolders
    folders_to_check = ['agent', 'configs', 'deps', 'launcher', 'logs', 'profiles']
    
    for folder in folders_to_check:
        folder_path = mlx_path / folder
        if folder_path.exists():
            print_success(f"  /{folder} - EXISTS")
        else:
            print_error(f"  /{folder} - NOT FOUND")
    
    # Check launcher in deps
    launcher_path = mlx_path / 'deps' / 'launcher'
    if launcher_path.exists():
        print_info(f"\nLauncher folder contents:")
        for item in launcher_path.iterdir():
            print(f"    {item.name}")

def check_logs():
    """Check recent log files"""
    print_header("CHECKING RECENT LOGS")
    
    username = os.getenv('USERNAME')
    logs_path = Path(f"C:/Users/{username}/mlx/logs")
    
    if not logs_path.exists():
        print_error(f"Logs folder not found at {logs_path}")
        return
    
    print_success(f"Logs folder found at {logs_path}")
    
    # List recent log files
    log_files = sorted(logs_path.glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if log_files:
        print_info(f"\nMost recent log files:")
        for log_file in log_files[:5]:
            size = log_file.stat().st_size
            print(f"  {log_file.name} ({size} bytes)")
            
        # Read last few lines of most recent log
        most_recent = log_files[0]
        print_info(f"\nLast 20 lines of {most_recent.name}:")
        try:
            with open(most_recent, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(f"    {line.rstrip()}")
        except Exception as e:
            print_error(f"Could not read log file: {e}")
    else:
        print_error("No log files found!")

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "MULTILOGIN LAUNCHER DIAGNOSTIC" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    
    check_multilogin_processes()
    check_launcher_process()
    check_ports()
    test_api_endpoints()
    check_mlx_folder()
    check_logs()
    
    print_header("DIAGNOSIS COMPLETE")
    print("\nPlease share this output with the support team!")
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
