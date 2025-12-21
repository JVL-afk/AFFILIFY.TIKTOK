# Quick Reference: Manual Profile Mapping

## 🎯 4-Step Setup (For Profiles Across 6 Accounts)

### Step 1: Generate CSV Template
```bash
python3 tools/build_csv_mapping.py \
    --proxies data/nodemaven_proxies.txt \
    --output data/profile_mapping.csv \
    --count 60
```

### Step 2: Extract Profile UUIDs
See: `tools/extract_profile_uuid.md`

**Quick Method:**
1. Open MultiLogin app
2. Right-click profile → Copy UUID
3. Paste into CSV file

### Step 3: Configure System
Edit `.env`:
```ini
MULTILOGIN_PROFILE_MODE=manual
PROFILE_MAPPING_CSV=data/profile_mapping.csv
```

### Step 4: Load Profiles
```bash
python3 pillar1_infrastructure/manual_profile_loader.py \
    --csv data/profile_mapping.csv
```

---

## ✅ Verification

Test one profile:
```bash
python3 test_profile_launch.py --profile-name TIKTOK1
```

---

## 📋 CSV Format

```csv
profile_name,profile_uuid,proxy_host,proxy_port,proxy_username,proxy_password,multilogin_account,notes
TIKTOK1,abc123-def456-ghi789,gate.nodemaven.com,8080,session_id_1,password_1,account1@example.com,US proxy
```

**Required:** profile_name, profile_uuid, proxy_host, proxy_port, proxy_username, proxy_password  
**Optional:** multilogin_account, notes

---

## 🚀 Run the System

```bash
# 1. Process videos
python3 pillar2_content_processing/main.py

# 2. Generate metadata
python3 pillar4_strategy/main.py

# 3. Start posting
python3 pillar5_distribution/main.py
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "CSV file missing required columns" | Use the template generator |
| "Profile UUID not found" | Check for spaces, verify UUID format |
| "Profile won't launch" | Ensure MultiLogin app is running, correct account logged in |
| "Wrong proxy" | Verify proxy credentials match profile configuration |

---

## 📚 Full Documentation

- **Complete Guide:** `MANUAL_SETUP_GUIDE.md`
- **UUID Extraction:** `tools/extract_profile_uuid.md`
- **Changelog:** `CHANGELOG_MANUAL_MAPPING.md`
- **Main README:** `README.md`

---

## 💡 Why Manual Mapping?

✅ **Most Secure** - No API credentials needed  
✅ **Multi-Account** - Works with profiles across 6+ accounts  
✅ **Simple** - Just a CSV file  
✅ **Transparent** - You control all data  

---

## 🎓 Pro Tips

1. **Extract UUIDs in batches of 10** to avoid mistakes
2. **Test one profile first** before loading all 60
3. **Keep CSV backups** in multiple secure locations
4. **Use version control** for the CSV file
5. **Document which account owns which profiles** in the notes column

---

**Need Help?** See `MANUAL_SETUP_GUIDE.md` for detailed instructions.
