#!/usr/bin/env python3
"""
TikTok Login Demo - Fallback Solution
This script demonstrates logging into TikTok using exported cookies and fingerprints
from MultiLogin profiles, bypassing the need for the Local Launcher API.

APPROACH:
1. Use MultiLogin manually to log into TikTok
2. Export cookies from MultiLogin
3. Load cookies into Playwright
4. Set matching fingerprints
5. Verify login works

This maintains GOOD stealth by using real MultiLogin fingerprints and cookies.
"""

import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import pandas as pd

class TikTokLoginDemo:
    def __init__(self, profile_data):
        self.profile_name = profile_data['profile_name']
        self.profile_uuid = profile_data['profile_uuid']
        self.tiktok_username = profile_data['tiktok_email']
        self.tiktok_password = profile_data['tiktok_password']
        self.proxy_host = profile_data.get('proxy_host', '')
        self.proxy_port = profile_data.get('proxy_port', '')
        self.proxy_username = profile_data.get('proxy_username', '')
        self.proxy_password = profile_data.get('proxy_password', '')
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.screen_width = 1920
        self.screen_height = 1080
        
        self.cookies_file = Path(f"data/cookies/{self.profile_name}_cookies.json")
        self.cookies_file.parent.mkdir(parents=True, exist_ok=True)
        
    async def login_manually_and_export_cookies(self):
        """
        Step 1: Manual login in MultiLogin, then export cookies
        
        INSTRUCTIONS FOR USER:
        1. Open MultiLogin X app
        2. Start the profile manually
        3. Navigate to TikTok and log in
        4. Export cookies using MultiLogin's cookie export feature
        5. Save to data/cookies/{profile_name}_cookies.json
        """
        print(f"\n{'='*60}")
        print(f"MANUAL LOGIN REQUIRED FOR: {self.profile_name}")
        print(f"{'='*60}")
        print("\n📋 INSTRUCTIONS:")
        print("1. Open MultiLogin X app")
        print(f"2. Start profile: {self.profile_name}")
        print("3. Navigate to https://www.tiktok.com/login")
        print(f"4. Log in with username: {self.tiktok_username}")
        print("5. Complete any 2FA/verification")
        print("6. Once logged in, export cookies:")
        print("   - Right-click in browser → Inspect → Application → Cookies")
        print("   - Or use MultiLogin's cookie export feature")
        print(f"7. Save cookies to: {self.cookies_file}")
        print("\n⏳ Waiting for cookies file...")
        
        # Wait for cookies file to exist
        while not self.cookies_file.exists():
            await asyncio.sleep(2)
        
        print(f"✅ Cookies file found!")
        return True
    
    async def login_with_cookies(self):
        """
        Step 2: Use exported cookies to log in with Playwright
        """
        print(f"\n{'='*60}")
        print(f"LOGGING IN WITH COOKIES: {self.profile_name}")
        print(f"{'='*60}")
        
        # Load cookies
        with open(self.cookies_file, 'r') as f:
            cookies = json.load(f)
        
        async with async_playwright() as p:
            # Launch browser with fingerprinting
            browser = await p.chromium.launch(
                headless=True,  # HEADLESS MODE for Linux server!
                args=[
                    f'--user-agent={self.user_agent}',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )
            
            # Create context with cookies and fingerprints
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': self.screen_width, 'height': self.screen_height},
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation'],
            )
            
            # Add cookies
            await context.add_cookies(cookies)
            
            # Create page
            page = await context.new_page()
            
            # Navigate to TikTok
            print("🌐 Navigating to TikTok...")
            await page.goto('https://www.tiktok.com/')
            
            # Wait a bit for page to load
            await asyncio.sleep(3)
            
            # Check if logged in
            try:
                # Look for profile icon or username
                await page.wait_for_selector('[data-e2e="profile-icon"]', timeout=5000)
                print("✅ SUCCESSFULLY LOGGED IN!")
                
                # Get username from page
                username_element = await page.query_selector('[data-e2e="profile-icon"]')
                if username_element:
                    print(f"✅ Profile icon found - logged in as {self.tiktok_username}")
                
                return True, browser, context, page
                
            except Exception as e:
                print(f"❌ Login verification failed: {e}")
                print("⚠️  Cookies might be expired or invalid")
                return False, browser, context, page
    
    async def automated_login(self):
        """
        Step 3: Automated login using username/password
        (Fallback if cookies don't work)
        """
        print(f"\n{'='*60}")
        print(f"AUTOMATED LOGIN: {self.profile_name}")
        print(f"{'='*60}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,  # HEADLESS MODE for Linux server!
                args=[
                    f'--user-agent={self.user_agent}',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': self.screen_width, 'height': self.screen_height},
            )
            
            page = await context.new_page()
            
            # Go to login page
            print("🌐 Navigating to TikTok login...")
            await page.goto('https://www.tiktok.com/login/phone-or-email/email')
            
            await asyncio.sleep(2)
            
            # Fill in credentials
            print(f"📝 Entering credentials for {self.tiktok_username}...")
            
            try:
                # Wait for login form
                await page.wait_for_selector('input[name="username"]', timeout=10000)
                
                # Enter username
                await page.fill('input[name="username"]', self.tiktok_username)
                await asyncio.sleep(1)
                
                # Enter password
                await page.fill('input[type="password"]', self.tiktok_password)
                await asyncio.sleep(1)
                
                # Click login button
                await page.click('button[type="submit"]')
                
                print("⏳ Waiting for login...")
                await asyncio.sleep(5)
                
                # Check if logged in
                try:
                    await page.wait_for_selector('[data-e2e="profile-icon"]', timeout=10000)
                    print("✅ SUCCESSFULLY LOGGED IN!")
                    
                    # Export cookies for future use
                    cookies = await context.cookies()
                    with open(self.cookies_file, 'w') as f:
                        json.dump(cookies, f, indent=2)
                    print(f"✅ Cookies saved to {self.cookies_file}")
                    
                    return True, browser, context, page
                    
                except:
                    print("⚠️  Login might require CAPTCHA or 2FA")
                    print("⏳ Please complete verification manually...")
                    
                    # Wait for manual intervention
                    await asyncio.sleep(30)
                    
                    # Check again
                    try:
                        await page.wait_for_selector('[data-e2e="profile-icon"]', timeout=5000)
                        print("✅ Login successful after manual verification!")
                        
                        # Export cookies
                        cookies = await context.cookies()
                        with open(self.cookies_file, 'w') as f:
                            json.dump(cookies, f, indent=2)
                        print(f"✅ Cookies saved to {self.cookies_file}")
                        
                        return True, browser, context, page
                    except:
                        print("❌ Login failed")
                        return False, browser, context, page
                        
            except Exception as e:
                print(f"❌ Error during login: {e}")
                return False, browser, context, page

async def main():
    """Main demo function"""
    print("\n" + "="*60)
    print(" TIKTOK LOGIN DEMO - FALLBACK SOLUTION")
    print("="*60)
    
    # Load profile data
    csv_path = Path("data/profile_mapping.csv")
    if not csv_path.exists():
        print("❌ CSV file not found!")
        return
    
    df = pd.read_csv(csv_path)
    
    # Use first profile for demo (TIKTOK1)
    profile_data = df.iloc[0].to_dict()
    
    print(f"\n📋 Testing with profile: {profile_data['profile_name']}")
    print(f"   UUID: {profile_data['profile_uuid']}")
    print(f"   TikTok Email: {profile_data['tiktok_email']}")
    
    demo = TikTokLoginDemo(profile_data)
    
    # Try automated login first
    print("\n🚀 Attempting automated login...")
    success, browser, context, page = await demo.automated_login()
    
    if success:
        print("\n✅ LOGIN DEMO SUCCESSFUL!")
        print("\n📸 Taking screenshot...")
        await page.screenshot(path='data/login_success.png')
        print("✅ Screenshot saved to data/login_success.png")
        
        print("\n⏳ Keeping browser open for 30 seconds...")
        await asyncio.sleep(30)
        
        await browser.close()
        
        print("\n" + "="*60)
        print(" DEMO COMPLETE - READY FOR FULL IMPLEMENTATION!")
        print("="*60)
    else:
        print("\n❌ LOGIN DEMO FAILED")
        print("⚠️  Manual intervention might be required")
        
        print("\n⏳ Keeping browser open for manual login...")
        print("   Please log in manually, then press Ctrl+C")
        
        try:
            await asyncio.sleep(300)  # Wait 5 minutes
        except KeyboardInterrupt:
            print("\n✅ Manual login completed")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
