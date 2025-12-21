# Affilify TikTok System - Complete Usage Guide

## 📋 Table of Contents

1. [First-Time Setup](#first-time-setup)
2. [Daily Workflow](#daily-workflow)
3. [Individual Pillar Usage](#individual-pillar-usage)
4. [Troubleshooting](#troubleshooting)
5. [Best Practices](#best-practices)

---

## 🚀 First-Time Setup

### Step 1: Install Dependencies

```bash
cd /home/ubuntu/affilify_tiktok_system

# Install Python packages
pip3 install -r requirements.txt

# Install Playwright browsers
sudo playwright install chromium

# Verify FFmpeg installation
ffmpeg -version
```

### Step 2: Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit configuration
nano .env
```

Fill in these required values:
```
MULTILOGIN_API_URL=https://api.multilogin.com
MULTILOGIN_API_TOKEN=your_actual_token_here
GEMINI_API_KEY=your_actual_gemini_key_here
```

### Step 3: Verify Proxy Data

```bash
# Check that proxy file exists and has 60+ proxies
wc -l data/nodemaven_proxies.txt
```

Should show 60 or more lines.

### Step 4: Create MultiLogin Profiles

```bash
# This creates all 60 profiles with unique proxies
python master_workflow.py --setup
```

**Expected output:**
```
Creating profile 1/60: TikTok_Account_01...
✅ Profile created successfully
Creating profile 2/60: TikTok_Account_02...
...
✅ All 60 profiles created successfully
```

**Time:** ~15-30 minutes

### Step 5: Manual TikTok Login (One-Time)

For each of the 60 MultiLogin profiles, you need to log in to TikTok once:

1. Open MultiLogin application
2. Launch profile "TikTok_Account_01"
3. Navigate to tiktok.com
4. Log in with your account credentials
5. Complete any 2FA/verification
6. Close the browser (session is saved)
7. Repeat for all 60 profiles

**Time:** ~2-4 hours (can be delegated to team members)

---

## 📅 Daily Workflow

### Option A: Fully Automated Daily Run

```bash
python master_workflow.py --daily-run
```

This executes the complete pipeline:
1. ✅ Scrapes current TikTok trends
2. ✅ Processes any new raw videos
3. ✅ Generates optimized metadata
4. ✅ Posts to all 60 accounts
5. ✅ Scrapes performance metrics
6. ✅ Generates daily report

**Time:** ~1-2 hours
**Best run:** Early morning (6-8 AM)

### Option B: Manual Step-by-Step

For more control, run each pillar individually:

#### Morning (8 AM): Trend Analysis
```bash
cd pillar3_trend_intelligence
python main.py --full-pipeline
```

#### Morning (9 AM): Content Processing
```bash
# Place your raw video in data/raw_videos/
cd pillar2_content_processing
python main.py --input ../data/raw_videos/create_website_demo.mp4 --feature "Create Website"
```

#### Morning (10 AM): Metadata Generation
```bash
cd pillar4_content_strategy
python main.py --feature "Create Website" --trends-file ../data/trends/trends_latest.json
```

#### Afternoon (2 PM): Distribution
```bash
cd pillar5_distribution
python main.py --dry-run  # Test first
python main.py --execute  # Then execute
```

#### Next Day (2 PM): Analytics
```bash
cd pillar6_analytics
python main.py --full-analysis
```

#### Next Day (3 PM): Reporting
```bash
cd pillar7_reporting
python main.py --daily-report
```

---

## 🎯 Individual Pillar Usage

### Pillar 1: Infrastructure Management

**Create all profiles:**
```bash
cd pillar1_infrastructure
python profile_creator.py
```

**Check profile status:**
```bash
# TODO: Add profile status checker
```

### Pillar 2: Content Processing

**Process a single video:**
```bash
cd pillar2_content_processing
python main.py --input /path/to/video.mp4 --feature "AI Chatbot"
```

**Process all videos in a directory:**
```bash
python main.py --batch-dir ../data/raw_videos/
```

**Options:**
- `--feature`: Affilify feature name (required)
- `--num-clips`: Number of unique clips to generate (default: 60)
- `--output-dir`: Where to save processed videos

**Output:**
- 60 unique video files in `data/processed_videos/`
- Processing manifest JSON file
- Each video has unique hash

### Pillar 3: Trend Intelligence

**Scrape trends only:**
```bash
cd pillar3_trend_intelligence
python main.py --scrape
```

**Analyze trends only:**
```bash
python main.py --analyze --trends-file ../data/trends/trends_20231215.json
```

**Full pipeline (scrape + analyze):**
```bash
python main.py --full-pipeline
```

**Output:**
- `data/trends/trends_YYYYMMDD.json` - Raw trend data
- `data/trends/analysis_YYYYMMDD.json` - Gemini analysis

### Pillar 4: Metadata Generation

**Generate metadata for one feature:**
```bash
cd pillar4_content_strategy
python main.py --feature "Create Website" --trends-file ../data/trends/trends_latest.json
```

**Generate for all 12 features:**
```bash
python main.py --batch-all-features --trends-file ../data/trends/trends_latest.json
```

**Options:**
- `--feature`: Feature name
- `--trends-file`: Path to trends JSON
- `--num-variations`: Number of unique captions (default: 60)

**Output:**
- `data/metadata/create_website_metadata.json`
- Contains 60 unique caption/hashtag combinations

### Pillar 5: Distribution

**Dry run (test without posting):**
```bash
cd pillar5_distribution
python main.py --dry-run
```

**Execute posting:**
```bash
python main.py --execute
```

**Schedule only (don't post yet):**
```bash
python main.py --schedule-only
```

**Options:**
- `--dry-run`: Test mode, no actual posting
- `--execute`: Live posting mode
- `--schedule-only`: Create schedule without executing
- `--accounts`: Specific account IDs to use (comma-separated)

**Safety features:**
- Randomized posting times (spread over 12 hours)
- Human-like delays between actions
- Automatic retry on failure
- Account health checks before posting

### Pillar 6: Analytics

**Scrape performance metrics:**
```bash
cd pillar6_analytics
python main.py --scrape
```

**Run optimization analysis:**
```bash
python main.py --optimize
```

**Full analysis (scrape + optimize):**
```bash
python main.py --full-analysis
```

**Output:**
- Updated database with performance metrics
- `data/reports/optimization_report_YYYYMMDD.json`

### Pillar 7: Reporting

**Generate daily report:**
```bash
cd pillar7_reporting
python main.py --daily-report
```

**Generate video requests only:**
```bash
python main.py --video-requests
```

**Output:**
- `data/reports/daily_report_YYYYMMDD.json` - Machine-readable
- `data/reports/daily_report_YYYYMMDD.txt` - Human-readable
- Console output with key metrics

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
pip3 install -r requirements.txt
```

### Issue: "MultiLogin API authentication failed"

**Causes:**
1. Invalid API token
2. Expired subscription
3. Wrong API URL

**Solution:**
```bash
# Check .env file
cat .env | grep MULTILOGIN

# Test API manually
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.multilogin.com/profiles
```

### Issue: "Video processing fails"

**Causes:**
1. FFmpeg not installed
2. Corrupted video file
3. Unsupported format

**Solution:**
```bash
# Check FFmpeg
ffmpeg -version

# Test video file
ffmpeg -i your_video.mp4

# Convert to supported format
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4
```

### Issue: "Posting fails - login required"

**Cause:** TikTok session expired in MultiLogin profile

**Solution:**
1. Open MultiLogin
2. Launch the failing profile
3. Navigate to tiktok.com
4. Log in again
5. Try posting again

### Issue: "Trend scraping fails"

**Causes:**
1. TikTok Creative Center HTML changed
2. Network connectivity issues
3. Playwright not installed

**Solution:**
```bash
# Reinstall Playwright
sudo playwright install chromium

# Test manually
playwright open https://ads.tiktok.com/business/creativecenter
```

### Issue: "Database locked"

**Cause:** Multiple processes accessing database simultaneously

**Solution:**
```bash
# Stop all running processes
pkill -f master_workflow.py

# Wait 10 seconds, then retry
```

---

## 💡 Best Practices

### Content Creation

1. **Video Length:** 30-90 seconds optimal
2. **Quality:** 1080p minimum
3. **Format:** MP4 (H.264 codec)
4. **Content:** Show actual Affilify features in action
5. **Variety:** Create different videos for each feature

### Posting Strategy

1. **Timing:** Post during peak hours (2-4 PM, 7-9 PM)
2. **Frequency:** 1 post per account per day maximum
3. **Variety:** Rotate features across accounts
4. **Consistency:** Post daily for best algorithm performance

### Account Management

1. **Warm-up:** Start with lower posting frequency for new accounts
2. **Monitoring:** Check daily reports for flagged accounts
3. **Rotation:** If an account gets flagged, pause it for 7 days
4. **Backup:** Always have 10-20 backup accounts ready

### Optimization

1. **Daily Review:** Check optimization reports every day
2. **A/B Testing:** Try different caption styles
3. **Trend Alignment:** Always incorporate current trending hashtags
4. **Feature Focus:** Double down on best-performing features

### Data Management

1. **Backups:** Backup database weekly
2. **Cleanup:** Archive old videos monthly
3. **Logs:** Review logs for errors
4. **Reports:** Save all daily reports

---

## 📊 Monitoring and Metrics

### Key Metrics to Track

1. **Daily Posts:** Should be 60 (1 per account)
2. **Average Views:** Target 1,000+ per video
3. **Engagement Rate:** Target 3%+
4. **Account Health:** 0 flagged accounts
5. **Conversion Rate:** Track sign-ups from TikTok traffic

### Where to Find Metrics

**Daily Summary:**
```bash
cd pillar7_reporting
python main.py --daily-report
```

**Detailed Analytics:**
```bash
cd pillar6_analytics
python main.py --full-analysis
```

**Database Query:**
```bash
sqlite3 data/affilify_system.db "SELECT COUNT(*) FROM videos WHERE posted_at > datetime('now', '-1 day');"
```

---

## 🔄 Maintenance Schedule

### Daily
- Run daily workflow
- Review daily report
- Check for flagged accounts

### Weekly
- Backup database
- Review optimization trends
- Create new raw videos based on requests

### Monthly
- Archive old data
- Review overall performance
- Adjust strategy based on learnings
- Update trending hashtags manually if needed

---

## 🎓 Advanced Usage

### Custom Scheduling

Edit `pillar5_distribution/posting_scheduler.py` to customize:
- Posting time windows
- Delay ranges
- Account rotation logic

### Custom Metadata Templates

Edit `pillar4_content_strategy/metadata_generator.py` to customize:
- Caption templates
- Hashtag strategies
- Call-to-action phrases

### Database Queries

```bash
# View all posts from last 7 days
sqlite3 data/affilify_system.db "SELECT * FROM videos WHERE posted_at > datetime('now', '-7 days');"

# View top performing videos
sqlite3 data/affilify_system.db "SELECT url, views, likes FROM analytics ORDER BY views DESC LIMIT 10;"

# View account health
sqlite3 data/affilify_system.db "SELECT profile_id, status, last_active FROM profiles;"
```

---

## 📞 Getting Help

1. **Check logs:** `tail -f logs/master_workflow.log`
2. **Review README:** `cat README.md`
3. **Test individual components:** Use `--test-pillar` flag
4. **Database inspection:** Use sqlite3 to query data

---

**You're now ready to run the Diamond Factory! 💎**
