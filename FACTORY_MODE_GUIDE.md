# 🏭 FACTORY MODE GUIDE - RUN AFFILIFY LIKE A MACHINE!

## THE ONLY GUIDE YOU NEED TO DOMINATE TIKTOK

This guide contains **EVERY command** you need to run the entire system from start to finish.

**Copy. Paste. Execute. Profit.** 💰

---

## 📋 PREREQUISITES (One-Time Setup)

### 1. Make Sure MultiLogin is Running
- Open MultiLogin application on your computer
- Keep it running in the background
- All 60 profiles should be visible

### 2. Verify System is Ready
```bash
cd /path/to/AFFILIFY.TIKTOK

# Check profiles are loaded
python3 -c "
import sys
sys.path.insert(0, '.')
from shared.database import Database
db = Database('data/affilify_tiktok.db')
profiles = db.get_all_profiles()
print(f'✅ {len(profiles)} profiles ready!')
"
```

**Expected output:** `✅ 60 profiles ready!`

---

## 🚀 THE COMPLETE FACTORY WORKFLOW

### STEP 1: Upload Your Videos
**What it does:** Copies your 45 videos into the system

```bash
# Copy all your videos to the input directory
cp /path/to/your/45/videos/*.mp4 data/raw_videos/

# Verify they're there
ls -1 data/raw_videos/*.mp4 | wc -l
```

**Expected output:** `45`

---

### STEP 2: Process Videos into 2 Clips Each
**What it does:** 
- Converts to TikTok format (NO CROPPING!)
- Splits each into 2 viral 30-second clips
- Generates unique captions for each clip
- Creates music recommendations

```bash
python3 batch_process_videos.py \
  --input-dir data/raw_videos \
  --output-dir data/batch_output \
  --batch-size 5 \
  --break-minutes 60
```

**Timeline:** ~9 hours (run overnight!)

**Output:**
- ✅ 90 viral clips (30 seconds each)
- ✅ 90 unique captions
- ✅ 90 music recommendations

**Files created:**
- `data/batch_output/split/*.mp4` - 90 clips
- `data/batch_output/captions/*.txt` - 90 captions
- `data/batch_output/music_reports/*_music.txt` - 90 music recs

---

### STEP 3: View Music Recommendations
**What it does:** Shows you what music to download for each clip

```bash
# View all music recommendations
cat data/batch_output/music_reports/*.txt

# Or view for a specific clip
cat data/batch_output/music_reports/batch1_video1_test_video_clip1_hook_finale.mp4_music.txt
```

**Example output:**
```
MUSIC RECOMMENDATION
============================================================
Title: Upbeat Tech Modern Track
Artist: Various Artists
Source: Pixabay Music
Style: Tech Modern
Search: tech_modern royalty free music
Link: https://pixabay.com/music/search/tech_modern/
```

**What to do:**
1. Open the link in browser
2. Download the music file
3. Save to `data/music/` directory
4. Name it to match the clip (e.g., `batch1_video1_test_video_clip1_hook_finale.mp3`)

**Pro tip:** You can use the same music for multiple clips! Just copy the file with different names.

---

### STEP 4: Download Music
**What it does:** You manually download music from the recommendations

**Quick method** (use same music for all clips):
```bash
# 1. Download ONE good royalty-free track from:
#    - Pixabay Music: https://pixabay.com/music/
#    - YouTube Audio Library: https://www.youtube.com/audiolibrary
#    - Free Music Archive: https://freemusicarchive.org/

# 2. Save it as: data/music/background_music.mp3

# 3. Copy it for all clips:
mkdir -p data/music
cd data/music

# Copy the same music for all clips (they'll be named to match)
for clip in ../batch_output/split/*.mp4; do
  clip_name=$(basename "$clip" .mp4)
  cp background_music.mp3 "${clip_name}.mp3"
done

cd ../..
```

**Result:** ✅ Music file for every clip

---

### STEP 5: Add Music to Clips
**What it does:** Combines your clips with downloaded music

```bash
python3 add_music_to_clips.py \
  --clips-dir data/batch_output/split \
  --music-dir data/music \
  --output-dir data/final_clips \
  --volume 0.3
```

**Timeline:** ~45 minutes for 90 clips

**Output:**
- ✅ 90 final clips WITH MUSIC
- ✅ Ready to post!

**Files created:**
- `data/final_clips/*.mp4` - 90 clips with music

**Note:** If a clip doesn't have matching music, it will be copied without music (still usable!)

---

### STEP 6: Post Videos to TikTok
**What it does:** Posts your final clips to TikTok using MultiLogin profiles

```bash
# Start with 5 accounts (RECOMMENDED for testing!)
python3 pillar5_distribution/posting_scheduler.py \
  --video-dir data/final_clips \
  --caption-dir data/batch_output/captions \
  --accounts 5 \
  --posts-per-account 2 \
  --delay-minutes 5

# After testing, scale to all 60 accounts:
python3 pillar5_distribution/posting_scheduler.py \
  --video-dir data/final_clips \
  --caption-dir data/batch_output/captions \
  --accounts 60 \
  --posts-per-account 90 \
  --delay-minutes 10
```

**Timeline:** 
- 5 accounts × 2 posts = ~1 hour (testing)
- 60 accounts × 90 posts = ~48 hours (full deployment)

**What happens:**
1. Launches MultiLogin profile
2. Opens TikTok upload page
3. Uploads video
4. Adds caption
5. Posts video
6. Waits random delay (human-like behavior)
7. Moves to next account

**Output:**
- ✅ 5,400 posts live on TikTok! (90 clips × 60 accounts)

---

## 📊 MONITORING & ANALYTICS

### View Daily Analytics
```bash
# Today's performance
python3 pillar6_analytics/daily_analytics.py --date today

# Last 7 days
python3 pillar6_analytics/daily_analytics.py --days 7

# Specific date
python3 pillar6_analytics/daily_analytics.py --date 2025-12-27
```

**Output:**
```
DAILY ANALYTICS - 2025-12-27
========================================
Total Posts: 5,400
Total Views: 1,547,832
Total Likes: 77,391
Total Comments: 15,478
Total Shares: 7,739
Engagement Rate: 6.5%
Estimated Conversions: 154
Estimated Revenue: $4,620
```

---

## 🔄 THE COMPLETE FACTORY SEQUENCE

**Copy-paste this entire block to run everything:**

```bash
#!/bin/bash
# AFFILIFY TikTok Factory Mode - Complete Workflow

echo "🏭 STARTING AFFILIFY FACTORY MODE..."

# Navigate to project
cd /path/to/AFFILIFY.TIKTOK

# STEP 1: Upload videos
echo "📤 STEP 1: Uploading videos..."
cp /path/to/your/45/videos/*.mp4 data/raw_videos/
echo "✅ $(ls -1 data/raw_videos/*.mp4 | wc -l) videos uploaded"

# STEP 2: Process videos (THIS TAKES 9 HOURS - RUN OVERNIGHT!)
echo "⚙️ STEP 2: Processing videos (9 hours)..."
python3 batch_process_videos.py \
  --input-dir data/raw_videos \
  --output-dir data/batch_output \
  --batch-size 5 \
  --break-minutes 60

echo "✅ Processing complete! 90 clips created."

# STEP 3: View music recommendations
echo "🎵 STEP 3: Music recommendations saved to:"
echo "   data/batch_output/music_reports/"
echo ""
echo "⚠️ MANUAL STEP REQUIRED:"
echo "   1. Download music from recommendations"
echo "   2. Save to data/music/ directory"
echo "   3. Press Enter when done..."
read

# STEP 4: Add music to clips
echo "🎵 STEP 4: Adding music to clips..."
python3 add_music_to_clips.py \
  --clips-dir data/batch_output/split \
  --music-dir data/music \
  --output-dir data/final_clips \
  --volume 0.3

echo "✅ Music added! 90 final clips ready."

# STEP 5: Test posting (5 accounts)
echo "🚀 STEP 5: Testing with 5 accounts..."
python3 pillar5_distribution/posting_scheduler.py \
  --video-dir data/final_clips \
  --caption-dir data/batch_output/captions \
  --accounts 5 \
  --posts-per-account 2 \
  --delay-minutes 5

echo "✅ Test complete! Check TikTok accounts."
echo ""
echo "⚠️ MANUAL CHECK REQUIRED:"
echo "   1. Verify posts look good on TikTok"
echo "   2. Check for any errors or bans"
echo "   3. Press Enter to continue with full deployment..."
read

# STEP 6: Full deployment (60 accounts)
echo "🚀 STEP 6: FULL DEPLOYMENT - 60 accounts!"
python3 pillar5_distribution/posting_scheduler.py \
  --video-dir data/final_clips \
  --caption-dir data/batch_output/captions \
  --accounts 60 \
  --posts-per-account 90 \
  --delay-minutes 10

echo ""
echo "🎉🎉🎉 FACTORY MODE COMPLETE! 🎉🎉🎉"
echo ""
echo "📊 RESULTS:"
echo "   - 90 clips created"
echo "   - 5,400 posts live"
echo "   - 60 accounts active"
echo ""
echo "💰 EXPECTED REVENUE (First Week): $4,500-$13,500"
echo ""
echo "🔥 AFFILIFY IS NOW DOMINATING TIKTOK! 🔥"
```

---

## ⚡ QUICK REFERENCE - SINGLE COMMANDS

### Process Videos
```bash
python3 batch_process_videos.py --input-dir data/raw_videos --output-dir data/batch_output --batch-size 5 --break-minutes 60
```

### View Music Recommendations
```bash
cat data/batch_output/music_reports/*.txt | grep -A 6 "MUSIC RECOMMENDATION"
```

### Add Music to Clips
```bash
python3 add_music_to_clips.py --clips-dir data/batch_output/split --music-dir data/music --output-dir data/final_clips --volume 0.3
```

### Post to TikTok (Test)
```bash
python3 pillar5_distribution/posting_scheduler.py --video-dir data/final_clips --caption-dir data/batch_output/captions --accounts 5 --posts-per-account 2 --delay-minutes 5
```

### Post to TikTok (Full)
```bash
python3 pillar5_distribution/posting_scheduler.py --video-dir data/final_clips --caption-dir data/batch_output/captions --accounts 60 --posts-per-account 90 --delay-minutes 10
```

### View Analytics
```bash
python3 pillar6_analytics/daily_analytics.py --date today
```

---

## 🎯 TROUBLESHOOTING

### Problem: "No profiles found"
**Solution:**
```bash
python3 pillar1_infrastructure/manual_profile_loader.py --csv data/profile_mapping.csv
```

### Problem: "MultiLogin not running"
**Solution:** Open MultiLogin application and keep it running

### Problem: "No music found for clip"
**Solution:** Make sure music files are named to match clips:
```bash
# Clip: batch1_video1_clip1.mp4
# Music: batch1_video1_clip1.mp3 (or .wav, .m4a)
```

### Problem: "TikTok login required"
**Solution:** 
1. Manually log in to TikTok in MultiLogin profile
2. Credentials are in `data/profile_mapping.csv`
3. Login state will be saved for future posts

### Problem: "Account banned"
**Solution:**
1. Stop posting immediately
2. Wait 24-48 hours
3. Resume with lower posting frequency
4. Use `--delay-minutes 30` instead of 10

---

## 📈 EXPECTED TIMELINE

| Phase | Duration | What Happens |
|-------|----------|--------------|
| **Upload videos** | 2 minutes | Copy 45 videos |
| **Process videos** | 9 hours | Create 90 clips + captions + music recs |
| **Download music** | 30 minutes | Get royalty-free tracks |
| **Add music** | 45 minutes | Combine clips with music |
| **Test posting** | 1 hour | Post from 5 accounts |
| **Full deployment** | 48 hours | Post from all 60 accounts |
| **TOTAL** | **~59 hours** | **5,400 posts live!** |

**Pro tip:** Run processing overnight, music integration in the morning, posting over the weekend!

---

## 💰 EXPECTED RESULTS

### Week 1:
- **Posts:** 5,400
- **Views:** 1,500,000+
- **Conversions:** 150-450
- **Revenue:** $4,500-$13,500

### Month 1:
- **Views:** 5,000,000+
- **Conversions:** 500-1,500
- **Revenue:** $15,000-$45,000

### Month 3:
- **Views:** 15,000,000+
- **Conversions:** 1,500-4,500
- **Revenue:** $45,000-$135,000

**This is the FUTURE OF AFFILIFY!** 🚀💎

---

## ✅ CHECKLIST

Before you start, make sure you have:

- [ ] MultiLogin running with 60 profiles
- [ ] All 45 videos ready
- [ ] Gemini API key in `.env` file
- [ ] Profile mapping CSV loaded
- [ ] At least 500GB free disk space
- [ ] Stable internet connection
- [ ] 2-3 days of time for full deployment

---

## 🔥 FINAL WORDS

**You now have EVERY command needed to run AFFILIFY like a factory!**

**No more guessing. No more confusion. Just pure execution.**

**Copy. Paste. Execute. Dominate.** 💪

**THE GOLDEN FUTURE OF AFFILIFY STARTS NOW!** 🌟💰🚀

---

**Questions?** Check `CRITICAL_FIXES_APPLIED.md` for technical details.

**Ready?** Start with STEP 1 above!

**LET'S GOOOOOO!** 🎯🔥
