# Quick Start: Using Your Existing MultiLogin Profiles

## 🎯 You Already Have Profiles? Perfect!

Since you've already created 60 MultiLogin profiles manually, here's the **fastest path** to get the system running:

---

## ⚡ 5-Minute Setup

### 1. Configure `.env` file

```bash
cp .env.template .env
nano .env  # or use your favorite editor
```

**Set these critical values:**

```bash
# MultiLogin credentials
MULTILOGIN_EMAIL=your_email@example.com
MULTILOGIN_PASSWORD=your_password
MULTILOGIN_AUTOMATION_TOKEN=your_token_here  # Get from MultiLogin settings
MULTILOGIN_PROFILE_MODE=existing  # ← IMPORTANT!

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key
```

### 2. Verify proxy file

```bash
# Check that your proxies are in the right place
cat data/nodemaven_proxies.txt | head -3

# Should show lines like:
# gate.nodemaven.com:8080:session_id:password
```

### 3. Load your existing profiles

```bash
# This extracts UUIDs from your MultiLogin account
python3 pillar1_infrastructure/profile_loader.py
```

**Expected output:**
```
✅ Found 60 TikTok profiles
✅ Created mapping for 60 profiles
✅ EXTRACTION COMPLETE!
```

### 4. Test one profile

```bash
# Quick test to make sure everything works
python3 test_profile_launch.py
```

**Expected output:**
```
✅ Profile started successfully!
✅ Profile stopped successfully!
```

---

## ✅ You're Ready!

Your existing profiles are now integrated with the system. Continue with the normal workflow:

### Next: Process Videos

```bash
# 1. Put raw videos in data/raw_videos/
# 2. Run the processor
python3 pillar2_content_processing/main.py
```

### Next: Generate Metadata

```bash
python3 pillar4_strategy/main.py
```

### Next: Start Posting

```bash
python3 pillar5_distribution/main.py
```

---

## 🔍 What Changed?

The system now:

1. **Searches** for your existing profiles (instead of creating new ones)
2. **Extracts** their UUIDs automatically
3. **Maps** each profile to a proxy
4. **Launches** profiles using MultiLogin's Local Launcher API

Everything else works exactly the same!

---

## 🚨 Troubleshooting

### "No profiles found"

- Make sure your profiles have "tiktok" in the name (case-insensitive)
- Check that your MultiLogin credentials are correct in `.env`

### "Failed to start profile"

- Make sure MultiLogin application is **running** on your machine
- Check that `https://launcher.mlx.yt:45001` is accessible

### "Authentication failed"

- Verify your `MULTILOGIN_EMAIL` and `MULTILOGIN_PASSWORD`
- Get a fresh `MULTILOGIN_AUTOMATION_TOKEN` from MultiLogin settings

---

## 📚 More Details

For a complete explanation of the migration process, see:
- **`MIGRATION_GUIDE.md`** - Full migration documentation
- **`USAGE_GUIDE.md`** - Complete system usage guide
- **`README.md`** - System overview and architecture

---

## 🎉 That's It!

You've successfully integrated your existing profiles. The system is now ready to distribute content across all 60 accounts!
