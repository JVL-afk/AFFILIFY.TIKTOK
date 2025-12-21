# Migration Guide: Using Existing MultiLogin Profiles

## Overview

This guide explains how to use the Affilify TikTok Content Distribution System with **existing MultiLogin profiles** that you've already created manually, instead of creating new profiles through the API.

**Good news:** You've already done the hard work! Since you created 60 MultiLogin profiles a week ago with proper geolocation and timezone matching, we just need to:

1. Extract the profile UUIDs from your MultiLogin account
2. Map each profile to a proxy credential
3. Configure the system to use these existing profiles

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **60 MultiLogin profiles** already created (you have these!)
- ✅ **65 Nodemaven proxy credentials** (you have these in `data/nodemaven_proxies.txt`)
- ✅ **MultiLogin application** installed and running on your machine
- ✅ **MultiLogin API token** (from your MultiLogin account settings)
- ✅ **Python 3.8+** installed
- ✅ **All dependencies** installed (`pip install -r requirements.txt`)

---

## Step 1: Configure Environment Variables

First, update your `.env` file with the correct settings for using existing profiles.

### 1.1 Copy the template

```bash
cp .env.template .env
```

### 1.2 Edit the `.env` file

Open `.env` in a text editor and configure these key settings:

```bash
# ============================================================================
# MULTILOGIN CONFIGURATION
# ============================================================================

# Cloud API (for profile search and management)
MULTILOGIN_API_BASE_URL=https://api.multilogin.com
MULTILOGIN_EMAIL=your_actual_email@example.com
MULTILOGIN_PASSWORD=your_actual_password

# Automation token (RECOMMENDED - get this from MultiLogin settings)
MULTILOGIN_AUTOMATION_TOKEN=your_automation_token_here

# Local Launcher API (for launching existing profiles)
MULTILOGIN_LAUNCHER_URL=https://launcher.mlx.yt:45001

# Profile Mode: Set to "existing" to use your manually created profiles
MULTILOGIN_PROFILE_MODE=existing

# ============================================================================
# GEMINI AI CONFIGURATION
# ============================================================================
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Important:** 
- The `MULTILOGIN_AUTOMATION_TOKEN` is highly recommended. Get it from your MultiLogin account settings.
- Make sure `MULTILOGIN_PROFILE_MODE=existing` (not "create")
- The `MULTILOGIN_LAUNCHER_URL` should be the default unless you changed it

---

## Step 2: Prepare Proxy Data

Your Nodemaven proxy credentials should already be in `data/nodemaven_proxies.txt`.

### 2.1 Verify the proxy file format

The file should contain one proxy per line in this format:

```
gate.nodemaven.com:8080:session_id_1:password_1
gate.nodemaven.com:8080:session_id_2:password_2
gate.nodemaven.com:8080:session_id_3:password_3
...
```

### 2.2 Check the file

```bash
head -5 data/nodemaven_proxies.txt
wc -l data/nodemaven_proxies.txt  # Should show 65 lines
```

---

## Step 3: Extract Profile UUIDs

Now we'll extract the UUIDs from your existing MultiLogin profiles.

### 3.1 Make sure MultiLogin is running

The MultiLogin application must be running on your machine for the Local Launcher API to work.

### 3.2 Run the profile loader script

```bash
cd /home/ubuntu/affilify_tiktok_system
python3 pillar1_infrastructure/profile_loader.py
```

This script will:
1. Connect to your MultiLogin account via the Cloud API
2. Search for all profiles with "tiktok" in the name
3. Extract their UUIDs and metadata
4. Map each profile to a proxy from your proxy list
5. Save everything to the database

### 3.3 Expected output

You should see output like this:

```
======================================================================
MULTILOGIN PROFILE LOADER - STARTING
======================================================================

Step 1: Loading proxy credentials...
  ✓ Loaded 65 proxies

Step 2: Searching for existing TikTok profiles in MultiLogin...
  🔍 Searching for profiles...
  Found 100 profiles (total: 100)
  ✓ Found 60 TikTok profiles

TikTok Profiles:
  1. TIKTOK1
  2. TIKTOK2
  3. TIKTOK3
  ...
  60. TIKTOK60

Step 3: Mapping profiles to proxies...
  Mapped TIKTOK1 -> US proxy
  Mapped TIKTOK2 -> GB proxy
  Mapped TIKTOK3 -> CA proxy
  ...

Step 4: Saving profile mapping...
  ✓ Saved TIKTOK1 to database
  ✓ Saved TIKTOK2 to database
  ...

======================================================================
✅ PROFILE LOADING COMPLETE!
======================================================================
Total profiles found: 60
Successfully loaded: 60
Failed: 0
======================================================================
```

### 3.4 Verify the results

Two files will be created:

1. **`data/profile_mapping.json`** - Human-readable mapping of profiles to proxies
2. **`data/affilify_system.db`** - SQLite database with all profile data

Check the mapping file:

```bash
cat data/profile_mapping.json | head -30
```

You should see JSON like this:

```json
{
  "TIKTOK1": {
    "uuid": "abc123-def456-ghi789",
    "folder_id": "folder_xyz",
    "proxy": {
      "host": "gate.nodemaven.com",
      "port": "8080",
      "username": "session_id_1",
      "password": "password_1",
      "country_code": "US"
    }
  },
  "TIKTOK2": {
    ...
  }
}
```

---

## Step 4: Test Profile Launching

Before running the full system, let's test that we can launch a profile.

### 4.1 Create a test script

Create `test_profile_launch.py`:

```python
#!/usr/bin/env python3
"""Test script to verify MultiLogin profile launching works."""

import os
import sys
from dotenv import load_dotenv
from pillar1_infrastructure.multilogin_client import MultiLoginClient
from shared.database import Database

# Load environment
load_dotenv()

# Initialize client
client = MultiLoginClient(
    base_url=os.getenv('MULTILOGIN_API_BASE_URL'),
    email=os.getenv('MULTILOGIN_EMAIL'),
    password=os.getenv('MULTILOGIN_PASSWORD'),
    automation_token=os.getenv('MULTILOGIN_AUTOMATION_TOKEN')
)

# Load database
db = Database(os.getenv('DATABASE_PATH', 'data/affilify_system.db'))

# Get first profile
profiles = db.get_all_profiles()
if not profiles:
    print("❌ No profiles found in database!")
    sys.exit(1)

test_profile = profiles[0]
print(f"Testing profile: {test_profile['profile_name']}")
print(f"UUID: {test_profile['profile_id']}")

# Try to start the profile
try:
    print("\n🚀 Starting profile...")
    connection_info = client.start_profile(
        profile_uuid=test_profile['profile_id'],
        automation_type="playwright"
    )
    
    print("✅ Profile started successfully!")
    print(f"WebSocket endpoint: {connection_info.get('ws_endpoint')}")
    print(f"HTTP debug port: {connection_info.get('http_debug_port')}")
    
    # Stop the profile
    print("\n🛑 Stopping profile...")
    client.stop_profile(test_profile['profile_id'])
    print("✅ Profile stopped successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
```

### 4.2 Run the test

```bash
python3 test_profile_launch.py
```

If successful, you should see:

```
Testing profile: TIKTOK1
UUID: abc123-def456-ghi789

🚀 Starting profile...
✅ Profile started successfully!
WebSocket endpoint: ws://127.0.0.1:12345/devtools/browser/...
HTTP debug port: 12345

🛑 Stopping profile...
✅ Profile stopped successfully!
```

---

## Step 5: Update the Main System

The system is now configured to use your existing profiles! Here's what changed:

### 5.1 Changes made to the system

1. **`pillar1_infrastructure/multilogin_client.py`**
   - Added `start_profile()` method for Local Launcher API
   - Added `stop_profile()` method for Local Launcher API
   - Added `get_active_profile_ports()` method

2. **`pillar1_infrastructure/profile_loader.py`** (NEW)
   - Replaces `profile_creator.py`
   - Loads existing profiles instead of creating new ones
   - Maps profiles to proxies

3. **`pillar5_distribution/tiktok_poster.py`**
   - Updated to use Local Launcher API
   - Connects to MultiLogin profiles via WebSocket
   - Properly manages profile lifecycle

4. **`shared/database.py`**
   - Added `get_profile_by_uuid()` method
   - Added `get_profile_by_name()` method

5. **`.env.template`**
   - Added `MULTILOGIN_LAUNCHER_URL` configuration
   - Added `MULTILOGIN_PROFILE_MODE` configuration

### 5.2 Workflow comparison

**OLD WORKFLOW (Creating Profiles):**
```
1. Parse proxy credentials
2. Create MultiLogin profiles via API
3. Store profile UUIDs in database
4. Launch profiles when needed
```

**NEW WORKFLOW (Using Existing Profiles):**
```
1. Parse proxy credentials
2. Search for existing profiles via API
3. Extract profile UUIDs
4. Map profiles to proxies
5. Store mappings in database
6. Launch profiles when needed
```

---

## Step 6: Run the Full System

Now you're ready to run the complete system!

### 6.1 Process videos (Pillar 2)

```bash
# Place your raw videos in data/raw_videos/
# Then run the video processor:
python3 pillar2_content_processing/main.py
```

### 6.2 Generate metadata (Pillar 4)

```bash
# Generate captions and hashtags for each video:
python3 pillar4_strategy/main.py
```

### 6.3 Start posting (Pillar 5)

```bash
# Start the posting scheduler:
python3 pillar5_distribution/main.py
```

The system will:
1. Load your existing profiles from the database
2. Launch each profile using the Local Launcher API
3. Connect via Playwright
4. Post videos to TikTok
5. Track performance

---

## Troubleshooting

### Problem: "No profiles found in database"

**Solution:** Run the profile loader again:
```bash
python3 pillar1_infrastructure/profile_loader.py
```

### Problem: "Failed to start MultiLogin profile"

**Possible causes:**
1. MultiLogin application is not running
2. Local Launcher API is not accessible
3. Profile UUID is incorrect

**Solution:**
1. Make sure MultiLogin is running on your machine
2. Check that `https://launcher.mlx.yt:45001` is accessible
3. Verify profile UUIDs in `data/profile_mapping.json`

### Problem: "Authentication failed"

**Solution:** Check your credentials in `.env`:
- `MULTILOGIN_EMAIL` is correct
- `MULTILOGIN_PASSWORD` is correct
- `MULTILOGIN_AUTOMATION_TOKEN` is valid (if using)

### Problem: "Profile names don't match"

If your profiles are not named "TIKTOK1", "TIKTOK2", etc., the system will still work! The profile loader searches for any profile with "tiktok" in the name (case-insensitive).

**To verify:** Check `data/profile_mapping.json` to see what names were detected.

### Problem: "More profiles than proxies" or "More proxies than profiles"

**Solution:** The system will automatically cycle through proxies if you have more profiles than proxies. If you have more proxies than profiles, some proxies won't be used.

---

## Advanced: Manual Profile Mapping

If you want to manually control which profile uses which proxy, you can edit the database directly.

### View current mappings

```bash
sqlite3 data/affilify_system.db "SELECT profile_name, proxy_host, proxy_username FROM multilogin_profiles;"
```

### Update a mapping

```bash
sqlite3 data/affilify_system.db "UPDATE multilogin_profiles SET proxy_username='new_session_id', proxy_password='new_password' WHERE profile_name='TIKTOK1';"
```

---

## Next Steps

Once your profiles are loaded and tested:

1. **Process your first batch of videos** (Pillar 2)
2. **Generate metadata** (Pillar 4)
3. **Start posting** (Pillar 5)
4. **Monitor analytics** (Pillar 6)
5. **Review daily reports** (Pillar 7)

Refer to the main `USAGE_GUIDE.md` for detailed instructions on each pillar.

---

## Summary

You've successfully migrated the system to use your existing MultiLogin profiles! The key changes were:

✅ Using the **Profile Search API** to find existing profiles  
✅ Using the **Local Launcher API** to launch profiles  
✅ Mapping profiles to proxies automatically  
✅ Storing everything in the database  

Your 60 profiles are now ready to distribute content at scale!

---

## Questions?

If you encounter any issues:

1. Check the logs in `logs/system.log`
2. Review the profile mapping in `data/profile_mapping.json`
3. Test individual profile launches with the test script
4. Verify MultiLogin is running and accessible

The system is designed to be resilient and will retry failed operations automatically.
