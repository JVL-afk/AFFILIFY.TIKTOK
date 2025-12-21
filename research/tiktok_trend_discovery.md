# TikTok Trend Discovery Research

## Key Findings

### Official TikTok Creative Center
- URL: https://ads.tiktok.com/business/creativecenter/pc/en
- Provides trending hashtags, songs, creators, and videos
- Data is publicly accessible (no login required for basic browsing)
- Organized by region (can filter by country)
- Categories: Hashtags, Songs, Creators, TikTok Videos

### Trend Intelligence Features
1. **Trending Hashtags** - Most popular hashtags by region
2. **Trending Songs** - Top audio tracks being used
3. **Trending Creators** - Most popular creators
4. **Trending Videos** - Top performing content

### Scraping Approaches

#### 1. TikTok Creative Center (Recommended)
- **Pros**: Official data, reliable, no authentication needed
- **Cons**: Rate limiting possible
- **Method**: Selenium/Playwright automation to scrape the Creative Center pages

#### 2. Third-Party APIs
- **Apify TikTok Scrapers**: Commercial solution
- **TikAPI**: Paid API service
- **ScrapeCreators**: API endpoint service
- **Cons**: Costs money, may have usage limits

#### 3. Direct TikTok Scraping
- **GitHub Projects**: 
  - drawrowfly/tiktok-scraper
  - bellingcat/tiktok-hashtag-analysis
- **Pros**: Free, open source
- **Cons**: May break with TikTok updates, requires maintenance

### Implementation Strategy for Pillar 3

**Approach**: Use Selenium/Playwright to scrape TikTok Creative Center

**Data to Collect**:
1. Top 20 trending hashtags (daily)
2. Top 20 trending songs (daily)
3. Top trending creators in relevant niches
4. Metadata: view counts, engagement rates, growth trends

**Storage**: SQLite database with daily snapshots

**Analysis**: Use Gemini Pro to:
- Identify which trends align with Affilify features
- Predict which trends will grow
- Generate content ideas based on trends
- Map trends to specific Affilify features

**Update Frequency**: Daily automated scraping
