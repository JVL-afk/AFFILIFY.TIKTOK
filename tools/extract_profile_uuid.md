# How to Extract Profile UUIDs from MultiLogin

Since your profiles are split across 6 MultiLogin accounts, you'll need to extract the UUID for each profile manually. This guide shows you how.

---

## Method 1: From MultiLogin Application (Easiest)

### Step 1: Open MultiLogin
Open the MultiLogin application on your computer.

### Step 2: Find Your Profile
Navigate to the profile you want to extract (e.g., TIKTOK1).

### Step 3: Right-click and Copy UUID
1. Right-click on the profile
2. Look for an option like "Copy Profile ID" or "Copy UUID"
3. Paste it into your CSV file

**Note:** The exact menu option may vary depending on your MultiLogin version.

---

## Method 2: From Profile Settings

### Step 1: Open Profile Settings
1. Right-click on the profile
2. Select "Settings" or "Edit Profile"

### Step 2: Find the UUID
The profile UUID is usually displayed at the top of the settings window or in an "Advanced" section.

### Step 3: Copy the UUID
Select and copy the UUID (it looks like: `abc123-def456-ghi789-jkl012`)

---

## Method 3: From Browser DevTools (Advanced)

If you can't find the UUID in the UI, you can extract it from the browser:

### Step 1: Launch the Profile
Start the MultiLogin profile you want to extract.

### Step 2: Open DevTools
In the launched browser, press `F12` to open DevTools.

### Step 3: Check the User Data Directory
1. Go to the Console tab
2. Type: `navigator.userAgent`
3. Or check the browser's profile directory path

The profile UUID is usually part of the user data directory path.

---

## Method 4: From MultiLogin API (If You Have Access)

If you have API access to one of your MultiLogin accounts:

### Step 1: Use the Profile Search API

```bash
curl -X POST https://api.multilogin.com/profile/search \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "offset": 0,
    "limit": 100,
    "search_text": "",
    "storage_type": "cloud"
  }'
```

### Step 2: Extract UUIDs from Response

The response will contain all profiles with their UUIDs:

```json
{
  "data": {
    "profiles": [
      {
        "uuid": "abc123-def456-ghi789-jkl012",
        "name": "TIKTOK1",
        ...
      }
    ]
  }
}
```

---

## Method 5: From Local Launcher API

If MultiLogin is running, you can query the Local Launcher API:

### Step 1: Check Active Profiles

```bash
curl https://launcher.mlx.yt:45001/api/v1/profile/active?profile_id=YOUR_PROFILE_UUID
```

**Note:** This requires you to already know the UUID, so it's more useful for verification.

---

## Creating Your CSV File

Once you have all the UUIDs, create your `profile_mapping.csv` file:

```csv
profile_name,profile_uuid,proxy_host,proxy_port,proxy_username,proxy_password,multilogin_account,notes
TIKTOK1,abc123-def456-ghi789-jkl012,gate.nodemaven.com,8080,session_id_1,password_1,account1@example.com,US proxy
TIKTOK2,bcd234-efg567-hij890-klm123,gate.nodemaven.com,8080,session_id_2,password_2,account1@example.com,GB proxy
TIKTOK3,cde345-fgh678-ijk901-lmn234,gate.nodemaven.com,8080,session_id_3,password_3,account2@example.com,CA proxy
...
```

### CSV Format Explanation

- **profile_name**: Your profile name (TIKTOK1, TIKTOK2, etc.)
- **profile_uuid**: The UUID you extracted from MultiLogin
- **proxy_host**: Usually `gate.nodemaven.com`
- **proxy_port**: Usually `8080`
- **proxy_username**: The session ID from your Nodemaven credentials
- **proxy_password**: The password from your Nodemaven credentials
- **multilogin_account**: (Optional) Which MultiLogin account owns this profile
- **notes**: (Optional) Any notes (e.g., "US proxy", "GB proxy")

---

## Tips

1. **Work in Batches**: Extract UUIDs for 10 profiles at a time to avoid mistakes
2. **Double-Check**: Make sure each UUID is unique
3. **Match Proxies**: Ensure each profile is matched with the correct proxy it was configured with
4. **Keep Backups**: Save a backup copy of your CSV file
5. **Test One First**: Load one profile first to make sure everything works

---

## Example Workflow

1. Open MultiLogin account #1
2. Extract UUIDs for profiles 1-10
3. Add them to `profile_mapping.csv`
4. Repeat for accounts #2-6
5. Load the CSV: `python3 pillar1_infrastructure/manual_profile_loader.py --csv data/profile_mapping.csv`
6. Test one profile: `python3 test_profile_launch.py --profile-name TIKTOK1`

---

## Troubleshooting

### "UUID not found"
- Make sure you copied the entire UUID
- Check for extra spaces or line breaks
- Verify the UUID format (should have dashes)

### "Profile won't launch"
- Make sure the MultiLogin account that owns this profile is logged in
- Verify the UUID is correct
- Check that MultiLogin application is running

### "Wrong proxy"
- Double-check that the proxy credentials match what was configured in the profile
- Verify the session ID is correct

---

## Need Help?

If you're having trouble extracting UUIDs:

1. Try Method 1 first (right-click in MultiLogin UI)
2. Check your MultiLogin version's documentation
3. Contact MultiLogin support for guidance on finding profile UUIDs
4. Use Method 4 (API) if you have access to at least one account

Once you have your CSV file ready, the system will handle everything else automatically!
