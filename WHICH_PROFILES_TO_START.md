# Which MultiLogin Profiles to Start?

## For Testing (5 Accounts)

When running with `--accounts 5`, you need to start these profiles in MultiLogin:

### Profiles to Start:
1. **TIKTOK1** (or TIKTOK 1)
2. **TIKTOK2** (or TIKTOK 2)
3. **TIKTOK3** (or TIKTOK 3)
4. **TIKTOK4** (or TIKTOK 4)
5. **TIKTOK5** (or TIKTOK 5)

## How to Start Profiles in MultiLogin

### Method 1: Manual Start (Recommended for Testing)
1. Open MultiLogin app
2. Find profiles TIKTOK1 through TIKTOK5
3. Right-click each profile → **Start**
4. Browser windows will open
5. Keep them open while running the posting script

### Method 2: Let the Script Start Them (Advanced)
The `post_to_tiktok.py` script can start profiles automatically using the Local Launcher API!

**However**, you need to make sure:
- MultiLogin app is running
- Local Launcher API is enabled (port 35000)
- Profiles are not already running

## For Full Deployment (60 Accounts)

When running with `--accounts 60`, you'll need:

### Option 1: Multiple PCs
- **PC 1:** Start TIKTOK1-TIKTOK20 (20 profiles)
- **PC 2:** Start TIKTOK21-TIKTOK40 (20 profiles)
- **PC 3:** Start TIKTOK41-TIKTOK60 (20 profiles)

### Option 2: Staggered Posting
Run the script multiple times:

**Batch 1:**
```bash
python3 post_to_tiktok.py --video-dir data/final_clips --caption-dir data/batch_output/captions --accounts 20 --posts-per-account 3 --delay-minutes 10
```
Start profiles: TIKTOK1-TIKTOK20

**Batch 2 (after Batch 1 completes):**
```bash
python3 post_to_tiktok.py --video-dir data/final_clips --caption-dir data/batch_output/captions --accounts 20 --posts-per-account 3 --delay-minutes 10
```
Start profiles: TIKTOK21-TIKTOK40

**Batch 3 (after Batch 2 completes):**
```bash
python3 post_to_tiktok.py --video-dir data/final_clips --caption-dir data/batch_output/captions --accounts 20 --posts-per-account 3 --delay-minutes 10
```
Start profiles: TIKTOK41-TIKTOK60

## Important Notes

### Profile Order
The script uses profiles in **alphabetical order** from the database:
- TIKTOK1, TIKTOK10, TIKTOK11, ..., TIKTOK19, TIKTOK2, TIKTOK20, ...

**OR** if your profiles are numbered:
- TIKTOK 1, TIKTOK 2, TIKTOK 3, ...

### Check Your Profile Names
Run this to see the exact order:
```bash
python3 << 'EOF'
from shared.database import Database
db = Database("data/affilify_tiktok.db")
profiles = db.get_all_profiles()
print("First 10 profiles:")
for i, p in enumerate(profiles[:10], 1):
    print(f"{i}. {p['name']} (UUID: {p['uuid'][:8]}...)")
EOF
```

### Resource Requirements
- **1 profile** = ~500MB RAM + 1 CPU core
- **5 profiles** = ~2.5GB RAM
- **20 profiles** = ~10GB RAM
- **60 profiles** = ~30GB RAM (need multiple PCs!)

## Quick Start Commands

### Step 1: Load Profiles into Database
```bash
python3 pillar1_infrastructure/manual_profile_loader.py --csv data/profile_mapping.csv
```

### Step 2: Start 5 Profiles in MultiLogin
Manually start TIKTOK1 through TIKTOK5

### Step 3: Run Posting Script
```bash
python3 post_to_tiktok.py \
  --video-dir data/final_clips \
  --caption-dir data/batch_output/captions \
  --accounts 5 \
  --posts-per-account 2 \
  --delay-minutes 5
```

## Troubleshooting

### "Profile not found"
- Make sure profile names in MultiLogin match database
- Check profile order with the Python script above

### "Cannot connect to profile"
- Make sure profiles are started in MultiLogin
- Check Local Launcher API is running (port 35000)

### "PC is too slow"
- Reduce number of accounts
- Close other applications
- Use multiple PCs for full deployment

---

**For testing: Just start TIKTOK1-TIKTOK5 manually!** 🚀
