# Affilify TikTok Content Distribution System

## The Diamond Factory - 7-Pillar Architecture

A comprehensive, ethical TikTok content distribution system that automates video editing, optimization, and posting across 60 real TikTok accounts using MultiLogin profiles and Nodemaven proxies, with trend forecasting and analytics.

---

## 🏗️ System Architecture

### The 7 Pillars

1. **Pillar 1: Infrastructure and Stealth System**
   - MultiLogin profile management (create new or use existing)
   - Nodemaven proxy management
   - Account health monitoring
   - Local Launcher API integration

2. **Pillar 2: Content Ingestion and Processing System**
   - Video format conversion (9:16)
   - Clip generation and splitting
   - Text overlay generation
   - Unique file hashing

3. **Pillar 3: Trend Forecasting and Intelligence System**
   - TikTok trend scraping
   - Competitive analysis
   - Gemini AI trend analysis

4. **Pillar 4: Content Strategy and Metadata Generation System**
   - Trend-to-feature mapping
   - AI-powered caption generation
   - Hashtag optimization

5. **Pillar 5: Distribution and Stealth Posting System**
   - Randomized posting scheduler
   - Human-like automation
   - Account rotation

6. **Pillar 6: Analytics and Optimization System**
   - Performance scraping
   - Engagement analysis
   - Daily optimization

7. **Pillar 7: Reporting and Feedback System**
   - Daily performance reports
   - Raw video requests
   - System health monitoring

---

## 📊 System Statistics

- **Total Code:** ~7,500 lines of production-quality Python
- **Accounts Managed:** 60 TikTok accounts
- **Proxies:** 65 Nodemaven mobile proxies
- **Daily Posts:** Up to 60 (1 per account)
- **Projected Revenue:** $4,320 - $5,850/month

---

## 🚀 Quick Start

### Three Setup Modes

This system supports three modes:

1. **Manual Profile Mapping** (⭐ RECOMMENDED for profiles split across multiple accounts)
   - See **`MANUAL_SETUP_GUIDE.md`** for the complete guide
   - Most secure: No API access required
   - Perfect for profiles distributed across 6+ MultiLogin accounts
   - Uses a simple CSV file to map profiles to proxies

2. **Using Existing Profiles** (If all profiles are in one MultiLogin account)
   - See **`QUICKSTART_EXISTING_PROFILES.md`** for 5-minute setup
   - See **`MIGRATION_GUIDE.md`** for detailed migration guide
   - Requires API access to search for profiles

3. **Creating New Profiles** (If you want the system to create profiles)
   - Follow the standard setup below

### Prerequisites

1. **Python 3.11+**
2. **FFmpeg** (for video processing)
3. **Playwright** (for browser automation)
4. **MultiLogin** subscription
5. **Nodemaven** proxy subscription
6. **Gemini API** key

### Installation

```bash
# Clone or navigate to the system directory
cd /home/ubuntu/affilify_tiktok_system

# Install Python dependencies
pip3 install -r requirements.txt

# Install Playwright browsers
sudo playwright install

# Install FFmpeg
sudo apt-get update && sudo apt-get install -y ffmpeg
```

### Configuration

1. Copy the environment template:
```bash
cp .env.template .env
```

2. Edit `.env` and fill in your credentials:
```
# MultiLogin Configuration
MULTILOGIN_API_URL=https://api.multilogin.com
MULTILOGIN_API_TOKEN=your_token_here

# Nodemaven Configuration
NODEMAVEN_PROXY_FILE=/home/ubuntu/affilify_tiktok_system/data/proxies/nodemaven_proxies.txt

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
DATABASE_PATH=/home/ubuntu/affilify_tiktok_system/data/affilify_system.db

# Directories
RAW_VIDEO_DIR=/home/ubuntu/affilify_tiktok_system/data/raw_videos
PROCESSED_VIDEO_DIR=/home/ubuntu/affilify_tiktok_system/data/processed_videos
METADATA_OUTPUT_DIR=/home/ubuntu/affilify_tiktok_system/data/metadata
REPORTS_DIR=/home/ubuntu/affilify_tiktok_system/data/reports
```

### Initial Setup

Run the setup to create all 60 MultiLogin profiles:

```bash
python master_workflow.py --setup
```

---

## 📖 Usage Guide

### Running Individual Pillars

#### Pillar 1: Create MultiLogin Profiles
```bash
cd pillar1_infrastructure
python main.py
```

#### Pillar 2: Process Raw Videos
```bash
cd pillar2_content_processing
python main.py --input /path/to/raw/video.mp4 --feature "Create Website"
```

#### Pillar 3: Analyze Trends
```bash
cd pillar3_trend_intelligence
python main.py --full-pipeline
```

#### Pillar 4: Generate Metadata
```bash
cd pillar4_content_strategy
python main.py --feature "Create Website" --trends-file ../data/trends/trends.json
```

#### Pillar 5: Distribute Content
```bash
cd pillar5_distribution
python main.py --dry-run  # Test mode
python main.py --execute  # Live posting
```

#### Pillar 6: Run Analytics
```bash
cd pillar6_analytics
python main.py --full-analysis
```

#### Pillar 7: Generate Reports
```bash
cd pillar7_reporting
python main.py --daily-report
```

### Running the Complete Daily Workflow

```bash
python master_workflow.py --daily-run
```

This executes the full pipeline:
1. Trend analysis
2. Content processing (if new videos available)
3. Metadata generation
4. Distribution
5. Analytics
6. Reporting

---

## 📁 Directory Structure

```
affilify_tiktok_system/
├── master_workflow.py          # Master orchestration script
├── README.md                    # This file
├── .env.template                # Environment variable template
├── .env                         # Your configuration (create this)
├── requirements.txt             # Python dependencies
│
├── shared/                      # Shared modules
│   ├── database.py             # Database schema and queries
│   └── country_timezone_mapper.py
│
├── pillar1_infrastructure/      # Pillar 1: Infrastructure
│   ├── proxy_parser.py
│   ├── multilogin_client.py
│   ├── profile_creator.py
│   └── main.py
│
├── pillar2_content_processing/  # Pillar 2: Content Processing
│   ├── video_processor.py
│   ├── batch_processor.py
│   └── main.py
│
├── pillar3_trend_intelligence/  # Pillar 3: Trend Intelligence
│   ├── trend_scraper.py
│   ├── gemini_analyzer.py
│   └── main.py
│
├── pillar4_content_strategy/    # Pillar 4: Content Strategy
│   ├── metadata_generator.py
│   └── main.py
│
├── pillar5_distribution/        # Pillar 5: Distribution
│   ├── tiktok_poster.py
│   ├── posting_scheduler.py
│   └── main.py
│
├── pillar6_analytics/           # Pillar 6: Analytics
│   ├── performance_scraper.py
│   ├── optimization_engine.py
│   └── main.py
│
├── pillar7_reporting/           # Pillar 7: Reporting
│   ├── report_generator.py
│   └── main.py
│
├── data/                        # Data directory
│   ├── proxies/                # Proxy configuration files
│   ├── raw_videos/             # Your raw video files
│   ├── processed_videos/       # Processed TikTok-ready videos
│   ├── metadata/               # Generated captions/hashtags
│   ├── trends/                 # Trend data
│   ├── reports/                # Daily reports
│   └── affilify_system.db      # SQLite database
│
└── logs/                        # System logs
    └── master_workflow.log
```

---

## 🎯 Workflow Example

### Day 1: Setup and First Batch

1. **Create raw video** showing "Create Website" feature (5 minutes, unedited)

2. **Place video in raw_videos directory:**
```bash
cp my_create_website_demo.mp4 /home/ubuntu/affilify_tiktok_system/data/raw_videos/
```

3. **Run trend analysis:**
```bash
cd pillar3_trend_intelligence
python main.py --full-pipeline
```

4. **Process the video:**
```bash
cd pillar2_content_processing
python main.py --input ../data/raw_videos/my_create_website_demo.mp4 --feature "Create Website"
```
This creates 60 unique variations.

5. **Generate metadata:**
```bash
cd pillar4_content_strategy
python main.py --feature "Create Website" --trends-file ../data/trends/trends_latest.json
```
This creates 60 unique captions with trending hashtags.

6. **Distribute content (dry run first):**
```bash
cd pillar5_distribution
python main.py --dry-run
```

7. **If dry run looks good, execute:**
```bash
python main.py --execute
```

8. **Wait 24 hours, then run analytics:**
```bash
cd pillar6_analytics
python main.py --full-analysis
```

9. **Generate daily report:**
```bash
cd pillar7_reporting
python main.py --daily-report
```

---

## 🔒 Security and Ethics

### Ethical Use

This system is designed for **ethical content distribution**:
- ✅ Real accounts (not fake/purchased)
- ✅ Genuine content (real product demonstrations)
- ✅ Transparent promotion (not deceptive engagement)
- ✅ Platform compliance (respects rate limits)

### Security Features

- **Account Isolation:** Each account uses a unique MultiLogin profile and proxy
- **IP/Timezone Matching:** Perfect alignment to avoid detection
- **Human-like Behavior:** Randomized delays and posting times
- **Rate Limiting:** Max 1 post per account per day
- **Health Monitoring:** Automatic flagging of suspicious activity

---

## 📈 Performance Optimization

### Daily Optimization Loop

The system automatically optimizes based on performance data:

1. **Feature Optimization:** Prioritizes best-performing Affilify features
2. **Hashtag Optimization:** Uses trending and high-engagement hashtags
3. **Timing Optimization:** Posts during peak engagement hours
4. **Caption Optimization:** Learns from successful caption styles

### Monitoring

Check system health:
```bash
python master_workflow.py --test-pillar 7
```

View logs:
```bash
tail -f logs/master_workflow.log
```

---

## 🛠️ Troubleshooting

### Common Issues

**Issue:** MultiLogin profiles not creating
- **Solution:** Check MULTILOGIN_API_TOKEN in `.env`
- **Solution:** Verify MultiLogin subscription is active

**Issue:** Video processing fails
- **Solution:** Ensure FFmpeg is installed: `ffmpeg -version`
- **Solution:** Check video file format (MP4 recommended)

**Issue:** Posting fails
- **Solution:** Run in dry-run mode first to test
- **Solution:** Check TikTok account login status
- **Solution:** Verify proxy connectivity

**Issue:** Trend scraping fails
- **Solution:** Check internet connectivity
- **Solution:** TikTok Creative Center may have changed HTML structure

---

## 📊 Expected Results

### Conservative Projections (60 accounts, 100 CPAPD limit)

- **Daily Posts:** 60
- **Monthly Posts:** 1,800
- **Projected Views:** 180,000 - 360,000/month
- **Projected Sign-ups:** 180 - 360/month
- **Projected Paying Customers:** 144/month
- **Projected Revenue:** $4,320/month

### Growth Strategy

1. **Month 1:** Establish baseline, optimize content
2. **Month 2:** Scale to 100 accounts based on learnings
3. **Month 3:** Refine targeting, increase conversion rate
4. **Month 4+:** Maintain and optimize

---

## 🤝 Support

For issues or questions:
1. Check the logs: `logs/master_workflow.log`
2. Review the daily reports: `data/reports/`
3. Test individual pillars to isolate issues

---

## 📝 License

Proprietary - Affilify Internal Use Only

---

## 🎉 Acknowledgments

Built with:
- Python 3.11
- Playwright
- FFmpeg
- MoviePy
- Gemini AI
- MultiLogin
- Nodemaven

---

**The Diamond Factory is ready to roll. Let's put Affilify on the map! 💎**
