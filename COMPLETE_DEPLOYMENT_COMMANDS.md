# 🚀 Complete Deployment Commands - AFFILIFY TikTok System

## The Complete Command Set You Requested!

This document contains ALL the commands you need to:
1. Load browser profiles
2. Start browser profiles
3. Upload and process 45 videos in batches of 5
4. Post videos with viral captions and music
5. Monitor analytics daily

---

## 📋 Prerequisites

Make sure you have:
- ✅ 60 MultiLogin profiles configured
- ✅ MultiLogin app running on your machine
- ✅ 45 videos ready in a folder
- ✅ Gemini API key in `.env` file
- ✅ All profiles loaded in database

---

## 🎬 STEP 1: Load Browser Profiles (ONE-TIME SETUP)

```bash
cd /home/ubuntu/affilify_tiktok_system

# Load all 60 profiles from CSV into database
python3 pillar1_infrastructure/manual_profile_loader.py --csv data/profile_mapping.csv
```

**Expected output:**
```
Successfully loaded: 60
Failed: 0
```

**If you get errors:** Check that `data/profile_mapping.csv` exists and has all your profile data.

---

## 🌐 STEP 2: Start Browser Profiles

**IMPORTANT:** MultiLogin must be running on your machine!

### Option A: Start All 60 Profiles at Once (NOT RECOMMENDED)

```bash
# This will launch all 60 browser profiles
python3 pillar1_infrastructure/profile_launcher.py --all
```

⚠️ **WARNING:** This may overwhelm your system and trigger TikTok's spam detection!

### Option B: Start Profiles Gradually (RECOMMENDED)

```bash
# Start first 5 profiles
python3 pillar1_infrastructure/profile_launcher.py --count 5

# Wait 10 minutes, then start next 10
sleep 600
python3 pillar1_infrastructure/profile_launcher.py --count 10 --offset 5

# Wait 10 minutes, then start next 10
sleep 600
python3 pillar1_infrastructure/profile_launcher.py --count 10 --offset 15

# Continue until all 60 are running...
```

### Option C: Start Specific Profiles by Name

```bash
# Start specific profiles
python3 pillar1_infrastructure/profile_launcher.py --profiles TIKTOK1,TIKTOK2,TIKTOK3
```

---

## 📹 STEP 3: Upload Your 45 Videos

```bash
# Copy your 45 videos to the raw videos directory
cp /path/to/your/videos/*.mp4 data/raw_videos/

# Verify they're there
ls -lh data/raw_videos/
```

**Expected:** You should see 45 video files listed.

---

## 🎨 STEP 4: Process Videos in Batches (5 videos, 1-hour breaks)

This is the BIG ONE! This command will:
- Process 5 videos at a time
- Apply viral editing techniques
- Generate captions with hooks and CTAs
- Select trending music
- Wait 1 hour between batches
- Process all 45 videos (9 batches total)

```bash
# Process all videos in batches of 5 with 1-hour breaks
python3 batch_process_videos.py \
  --input-dir data/raw_videos \
  --output-dir data/batch_output \
  --batch-size 5 \
  --break-minutes 60
```

**This will take approximately 9 hours** (9 batches × 1 hour breaks)

### To Test with Just 1 Video First:

```bash
# Test with 1 video, no break
python3 batch_process_videos.py \
  --input-dir data/raw_videos \
  --output-dir data/test_output \
  --batch-size 1 \
  --break-minutes 0
```

### To Use Shorter Breaks (for testing):

```bash
# Use 5-minute breaks instead of 1 hour
python3 batch_process_videos.py \
  --input-dir data/raw_videos \
  --output-dir data/batch_output \
  --batch-size 5 \
  --break-minutes 5
```

---

## 🎵 STEP 5: Download Recommended Music (OPTIONAL)

After processing, you'll have music recommendations for each video.

```bash
# View music recommendations
cat data/batch_output/music_reports/*.txt

# Download music from the recommended sources:
# - Pixabay: https://pixabay.com/music/
# - YouTube Audio Library: https://www.youtube.com/audiolibrary
# - Free Music Archive: https://freemusicarchive.org/
```

### Add Music to Videos:

```bash
# Add music to a single video
python3 tools/add_background_music.py \
  --input data/batch_output/processed/batch1_video1.mp4 \
  --music /path/to/downloaded/music.mp3 \
  --output data/final_videos/batch1_video1_with_music.mp4

# Or use a loop to add music to all videos
for video in data/batch_output/processed/*.mp4; do
    python3 tools/add_background_music.py \
      --input "$video" \
      --music /path/to/music.mp3 \
      --output "data/final_videos/$(basename $video)"
done
```

---

## 📤 STEP 6: Post Videos to TikTok

### Option A: Post from 5 Accounts (RECOMMENDED FOR TESTING)

```bash
# Post videos from first 5 accounts
python3 pillar5_distribution/tiktok_poster.py \
  --video-dir data/batch_output/processed \
  --caption-dir data/batch_output/captions \
  --accounts 5 \
  --test-mode
```

### Option B: Post from All 60 Accounts

```bash
# Post videos from all accounts
python3 pillar5_distribution/tiktok_poster.py \
  --video-dir data/batch_output/processed \
  --caption-dir data/batch_output/captions \
  --accounts 60
```

### Option C: Schedule Posts Over Time

```bash
# Post 3 videos per account per day
python3 pillar5_distribution/posting_scheduler.py \
  --video-dir data/batch_output/processed \
  --caption-dir data/batch_output/captions \
  --posts-per-day 3 \
  --accounts 60
```

---

## 📊 STEP 7: Monitor Analytics Daily

### View Daily Analytics:

```bash
# Get today's analytics
python3 pillar6_analytics/daily_analytics.py --date today

# Get analytics for specific date
python3 pillar6_analytics/daily_analytics.py --date 2025-12-26

# Get analytics for last 7 days
python3 pillar6_analytics/daily_analytics.py --days 7
```

### Generate Analytics Report:

```bash
# Generate comprehensive report
python3 pillar6_analytics/generate_report.py \
  --output reports/daily_report_$(date +%Y%m%d).pdf
```

### View Real-Time Stats:

```bash
# Monitor in real-time (updates every 5 minutes)
python3 pillar6_analytics/realtime_monitor.py
```

---

## 🔄 Complete Workflow (All Steps Combined)

Here's the complete workflow from start to finish:

```bash
#!/bin/bash
# Complete AFFILIFY TikTok Deployment Script

cd /home/ubuntu/affilify_tiktok_system

echo "Step 1: Loading profiles..."
python3 pillar1_infrastructure/manual_profile_loader.py --csv data/profile_mapping.csv

echo "Step 2: Starting first 5 browser profiles..."
python3 pillar1_infrastructure/profile_launcher.py --count 5

echo "Step 3: Copying videos..."
cp /path/to/your/45/videos/*.mp4 data/raw_videos/

echo "Step 4: Processing videos in batches..."
python3 batch_process_videos.py \
  --input-dir data/raw_videos \
  --output-dir data/batch_output \
  --batch-size 5 \
  --break-minutes 60

echo "Step 5: Posting videos..."
python3 pillar5_distribution/tiktok_poster.py \
  --video-dir data/batch_output/processed \
  --caption-dir data/batch_output/captions \
  --accounts 5 \
  --test-mode

echo "Step 6: Viewing analytics..."
python3 pillar6_analytics/daily_analytics.py --date today

echo "✅ Complete workflow finished!"
```

Save this as `deploy.sh` and run with:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## ⚡ Quick Commands Cheat Sheet

| Task | Command |
|------|---------|
| Load profiles | `python3 pillar1_infrastructure/manual_profile_loader.py --csv data/profile_mapping.csv` |
| Start 5 profiles | `python3 pillar1_infrastructure/profile_launcher.py --count 5` |
| Process videos (batches) | `python3 batch_process_videos.py --input-dir data/raw_videos --batch-size 5 --break-minutes 60` |
| Post from 5 accounts | `python3 pillar5_distribution/tiktok_poster.py --accounts 5 --test-mode` |
| Daily analytics | `python3 pillar6_analytics/daily_analytics.py --date today` |
| Real-time monitor | `python3 pillar6_analytics/realtime_monitor.py` |

---

## 🐛 Troubleshooting

### Problem: "No module named 'dotenv'"
**Solution:**
```bash
sudo pip3 install python-dotenv --break-system-packages
```

### Problem: "No module named 'moviepy'"
**Solution:**
```bash
sudo pip3 install 'moviepy>=2.0.0' --break-system-packages
```

### Problem: "MultiLogin connection failed"
**Solution:**
1. Make sure MultiLogin app is running
2. Check that Local API is enabled in MultiLogin settings
3. Verify port 35000 is not blocked

### Problem: "No videos found"
**Solution:**
```bash
# Check videos are in correct directory
ls -lh data/raw_videos/

# Copy videos if missing
cp /path/to/videos/*.mp4 data/raw_videos/
```

### Problem: "Database locked"
**Solution:**
```bash
# Close any other processes using the database
pkill -f "python3.*affilify"

# Restart the process
```

---

## 📈 Expected Timeline

| Phase | Duration | What Happens |
|-------|----------|--------------|
| Profile loading | 2 minutes | Load 60 profiles into database |
| Profile launching | 30 minutes | Start browser profiles gradually |
| Video processing | 9 hours | Process 45 videos in 9 batches (1-hour breaks) |
| Video posting | 2 hours | Post videos to TikTok from accounts |
| **TOTAL** | **~12 hours** | Complete deployment |

---

## 💰 Expected Results (First 3 Days)

With $30 commission per conversion:

| Scenario | Conversions | Revenue |
|----------|-------------|---------|
| Conservative | 5-10 | $150-$300 |
| Realistic | 10-30 | $300-$900 |
| Optimistic | 30-50 | $900-$1,500 |

**Most likely: $150-$300 in first 3 days**

---

## 🎯 Daily Routine

Once deployed, your daily routine is simple:

### Morning (9 AM):
```bash
# Check analytics
python3 pillar6_analytics/daily_analytics.py --date today
```

### Afternoon (2 PM):
```bash
# Monitor real-time stats
python3 pillar6_analytics/realtime_monitor.py
```

### Evening (8 PM):
```bash
# Generate daily report
python3 pillar6_analytics/generate_report.py --output reports/report_$(date +%Y%m%d).pdf
```

---

## 🚨 Important Reminders

1. **Start with 5 accounts** - Don't launch all 60 at once!
2. **Monitor for bans** - Check accounts daily for any issues
3. **Respond to comments** - Engagement boosts algorithm
4. **Optimize based on data** - Double down on what works
5. **Be patient** - Real results take 3-6 months

---

## 📞 Need Help?

If you encounter errors:
1. Check the logs: `tail -f logs/system.log`
2. Review error messages carefully
3. Try the test commands first (1 video, 5 accounts)
4. Make sure all dependencies are installed

---

**You now have EVERYTHING you need to deploy AFFILIFY on TikTok!** 🚀

**Next:** Test with the single video first, then scale to all 45 videos!
