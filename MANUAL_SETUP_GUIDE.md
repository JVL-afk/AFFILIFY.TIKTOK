> **Security First**: This guide is for users who have profiles split across multiple MultiLogin accounts. This method is more secure as it does not require API access to your accounts.

# Manual Setup Guide: For Profiles Across Multiple Accounts

This guide explains how to configure the system by manually providing a list of your profile UUIDs and their corresponding proxy information. This is the recommended approach for maximum security, especially when your 60 profiles are distributed across 6 different MultiLogin accounts.

**The core idea is simple**: You create a single CSV file that tells the system everything it needs to know to launch your profiles, without needing to access your MultiLogin accounts via the API.

---

##  Workflow Overview

Here is the 4-step process:

1.  **Generate a Template**: Use a helper script to create a pre-filled CSV file from your list of 65 Nodemaven proxies.
2.  **Extract & Add UUIDs**: Manually get the unique ID (UUID) for each of your 60 profiles from the MultiLogin application and add them to the CSV.
3.  **Configure the System**: Update the `.env` file to use the new "manual" mode.
4.  **Load the Data**: Run a script to load your completed CSV file into the system's database.

---

## Step 1: Generate Your CSV Template

First, we will create a CSV file that is already populated with your 65 Nodemaven proxy credentials. This saves you from having to copy and paste them manually.

```bash
# Navigate to the system directory
cd /home/ubuntu/affilify_tiktok_system

# Run the CSV builder tool
python3 tools/build_csv_mapping.py \
    --proxies data/nodemaven_proxies.txt \
    --output data/profile_mapping.csv \
    --count 60
```

This command will create a new file at `data/profile_mapping.csv` with 60 rows, one for each of your TikTok profiles. Each row will have a placeholder for the profile UUID.

**Your generated CSV will look like this:**

| profile_name | profile_uuid          | proxy_host         | proxy_port | proxy_username | proxy_password | multilogin_account | notes     |
| :----------- | :-------------------- | :----------------- | :--------- | :------------- | :------------- | :----------------- | :-------- |
| TIKTOK1      | REPLACE_WITH_UUID_1   | gate.nodemaven.com | 8080       | session_id_1   | password_1     |                    | Proxy 1   |
| TIKTOK2      | REPLACE_WITH_UUID_2   | gate.nodemaven.com | 8080       | session_id_2   | password_2     |                    | Proxy 2   |
| ...          | ...                   | ...                | ...        | ...            | ...            |                    | ...       |

---

## Step 2: Extract and Add Profile UUIDs

Now for the most important part. You need to get the unique ID (UUID) for each of your 60 profiles from within the MultiLogin application.

**I have created a detailed guide and a helper script to make this easy.** Please open and follow the instructions in:

> **`tools/extract_profile_uuid.md`**

This guide provides several methods to get the UUIDs, including a simple right-click in the MultiLogin app and a JavaScript bookmarklet you can run in your browser.

**Your task:**

1.  Open `data/profile_mapping.csv` in a spreadsheet editor (like Google Sheets, Excel, or LibreOffice Calc).
2.  For each profile (TIKTOK1, TIKTOK2, etc.), find its UUID in the MultiLogin app.
3.  Replace the `REPLACE_WITH_UUID_...` placeholder with the actual UUID.
4.  (Optional) In the `multilogin_account` column, you can add a note for yourself indicating which of your 6 accounts owns that profile.
5.  Save the CSV file.

**After editing, your CSV should look like this:**

| profile_name | profile_uuid                 | ... |
| :----------- | :--------------------------- | :- |
| TIKTOK1      | `abc12345-abcd-1234-5678-abcde1234567` | ... |
| TIKTOK2      | `def67890-abcd-1234-5678-abcde1234567` | ... |

---

## Step 3: Configure the System for Manual Mode

Next, tell the system to use your manually created CSV file instead of the API.

1.  **Copy the template if you haven't already**:
    ```bash
    cp .env.template .env
    ```

2.  **Edit the `.env` file** and set the following:

    ```ini
    # Profile Mode: "manual", "existing", or "create"
    # Use "manual" for profiles split across multiple accounts.
    MULTILOGIN_PROFILE_MODE=manual

    # CSV Mapping File (only used in "manual" mode)
    PROFILE_MAPPING_CSV=data/profile_mapping.csv

    # You can leave these blank in manual mode, as they are not used.
    MULTILOGIN_EMAIL=
    MULTILOGIN_PASSWORD=
    MULTILOGIN_AUTOMATION_TOKEN=
    ```

By setting `MULTILOGIN_PROFILE_MODE` to `manual`, you are disabling all API-based profile searching, making the system more secure.

---

## Step 4: Load Your Profile Data

Finally, run the manual loader script to import your completed CSV file into the system's database.

```bash
python3 pillar1_infrastructure/manual_profile_loader.py --csv data/profile_mapping.csv
```

**Expected Output:**

```
MANUAL PROFILE LOADER - STARTING
======================================================================
Loading profiles from CSV: data/profile_mapping.csv
✅ Loaded 60 profiles from CSV

Saving profiles to database...
  ✓ Saved TIKTOK1 to database
  ✓ Saved TIKTOK2 to database
  ...
✅ PROFILE LOADING COMPLETE!
======================================================================
Total profiles in CSV: 60
Successfully loaded: 60
Failed: 0
```

---

## Verification: Test a Profile Launch

Before running the full system, it is highly recommended to test that a single profile can be launched correctly. This confirms your UUIDs are correct and the Local Launcher API is working.

**Important**: For this to work, the MultiLogin application must be running on your machine, and you must be logged into the account that owns the profile you are testing.

```bash
# Test the first profile in your list (TIKTOK1)
python3 test_profile_launch.py --profile-name TIKTOK1
```

If successful, you will see the MultiLogin browser for TIKTOK1 launch and then close automatically.

---

## You Are Ready!

That's it! You have successfully configured the system to use your 60 profiles from 6 different accounts without exposing any API keys. The system will now use the UUIDs from the database to launch the correct profiles for posting.

You can now proceed with the standard workflow:

1.  **Process Videos**: `python3 pillar2_content_processing/main.py`
2.  **Generate Metadata**: `python3 pillar4_strategy/main.py`
3.  **Start Posting**: `python3 pillar5_distribution/main.py`

Refer to the main `USAGE_GUIDE.md` for more details on operating the 7-Pillar system.
