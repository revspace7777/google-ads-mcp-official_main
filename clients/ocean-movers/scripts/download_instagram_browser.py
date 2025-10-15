#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download all media from Jacksonville Moving and Storage Instagram
Profile: @jacksonvillemovingandstorage
Using browser automation to extract media URLs directly
"""

import sys
import io
import os
import json
import time
import random
import asyncio
import requests
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import playwright
from playwright.async_api import async_playwright

# Configuration
INSTAGRAM_USERNAME = "heathevanmartin"
INSTAGRAM_PASSWORD = "Light&Earth_surr3nder@77"
TARGET_PROFILE = "jacksonvillemovingandstorage"
MEDIA_DIR = Path(__file__).parent.parent / "media" / TARGET_PROFILE

async def login_to_instagram(page):
    """Login to Instagram"""
    print("Navigating to Instagram...")
    
    try:
        await page.goto('https://www.instagram.com/', timeout=30000)
        await asyncio.sleep(4)
        
        # Check if already logged in
        if '/accounts/login' not in page.url:
            print("Already logged in!")
            return True
        
        print("Logging in...")
        
        # Fill username
        await page.fill('input[name="username"]', INSTAGRAM_USERNAME, timeout=10000)
        await asyncio.sleep(0.8)
        
        # Fill password
        await page.fill('input[name="password"]', INSTAGRAM_PASSWORD, timeout=10000)
        await asyncio.sleep(1.2)
        
        # Click login
        await page.click('button[type="submit"]', timeout=10000)
        await asyncio.sleep(8)
        
        # Handle save login dialog
        try:
            await page.click('button:has-text("Not now")', timeout=5000)
            await asyncio.sleep(2)
        except:
            pass
        
        # Handle notifications dialog
        try:
            await page.click('button:has-text("Not Now")', timeout=5000)
            await asyncio.sleep(2)
        except:
            pass
        
        print("Login successful!")
        return True
        
    except Exception as e:
        print(f"Login error: {e}")
        return False

async def extract_media_urls_from_page(page):
    """Extract all media URLs visible on the page using JavaScript"""
    media_urls = await page.evaluate('''
        () => {
            const urls = new Set();
            
            // Get all images
            document.querySelectorAll('article img').forEach(img => {
                if (img.src && img.src.includes('instagram') && !img.src.includes('s150x150')) {
                    urls.add(img.src);
                }
            });
            
            // Get all videos
            document.querySelectorAll('article video').forEach(video => {
                if (video.src) {
                    urls.add(video.src);
                }
            });
            
            return Array.from(urls);
        }
    ''')
    
    return media_urls

async def scroll_and_load_all_posts(page, max_scrolls=50):
    """Scroll profile to load all posts"""
    print("Scrolling to load all posts...")
    
    all_media_urls = set()
    last_height = 0
    stall_count = 0
    
    for scroll in range(max_scrolls):
        # Extract media from current view
        media_urls = await extract_media_urls_from_page(page)
        
        before_count = len(all_media_urls)
        all_media_urls.update(media_urls)
        after_count = len(all_media_urls)
        new_items = after_count - before_count
        
        print(f"  Scroll {scroll + 1}: Found {new_items} new media (total: {after_count})")
        
        # Scroll down
        await page.evaluate('window.scrollBy(0, window.innerHeight * 0.8)')
        await asyncio.sleep(random.uniform(1.5, 2.5))
        
        # Check if we're stuck
        new_height = await page.evaluate('document.body.scrollHeight')
        if new_height == last_height and new_items == 0:
            stall_count += 1
            if stall_count >= 3:
                print("  Reached end of profile")
                break
        else:
            stall_count = 0
            last_height = new_height
    
    return list(all_media_urls)

def download_file(url, filepath, index):
    """Download a single file"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

async def main():
    print("=" * 80)
    print("INSTAGRAM MEDIA DOWNLOADER")
    print(f"Profile: @{TARGET_PROFILE}")
    print("=" * 80)
    print()
    
    # Create media directory
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Media directory: {MEDIA_DIR}")
    print()
    
    async with async_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Login
        success = await login_to_instagram(page)
        if not success:
            print("Login failed!")
            await browser.close()
            return
        
        # Navigate to target profile
        print(f"\nNavigating to @{TARGET_PROFILE}...")
        await page.goto(f'https://www.instagram.com/{TARGET_PROFILE}/', timeout=45000)
        await asyncio.sleep(random.uniform(4, 6))
        
        # Get profile stats
        try:
            stats = await page.evaluate('''
                () => {
                    const posts = document.querySelector('a[href*="/p/"]')?.closest('li')?.querySelector('span')?.textContent || '0';
                    return { posts };
                }
            ''')
            print(f"Profile has {stats['posts']} posts")
        except:
            print("Could not read profile stats")
        
        print()
        
        # Scroll and collect all media URLs
        all_media_urls = await scroll_and_load_all_posts(page)
        
        print()
        print(f"Total media URLs collected: {len(all_media_urls)}")
        print()
        
        # Download all media
        print("=" * 80)
        print("DOWNLOADING MEDIA FILES")
        print("=" * 80)
        print()
        
        downloaded = 0
        errors = 0
        
        for idx, url in enumerate(all_media_urls, 1):
            # Determine if image or video
            extension = '.mp4' if '/v/' in url or '.mp4' in url else '.jpg'
            filename = f"media_{idx:04d}{extension}"
            filepath = MEDIA_DIR / filename
            
            print(f"[{idx}/{len(all_media_urls)}] Downloading {filename}...")
            
            if download_file(url, filepath, idx):
                downloaded += 1
                print(f"    Saved!")
            else:
                errors += 1
        
        # Save metadata
        metadata = {
            'profile': TARGET_PROFILE,
            'download_date': datetime.now().isoformat(),
            'total_media': len(all_media_urls),
            'downloaded': downloaded,
            'errors': errors,
            'media_urls': all_media_urls
        }
        
        metadata_file = MEDIA_DIR / 'download_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Summary
        print()
        print("=" * 80)
        print("DOWNLOAD COMPLETE")
        print("=" * 80)
        print(f"Total media URLs found: {len(all_media_urls)}")
        print(f"Successfully downloaded: {downloaded}")
        print(f"Errors: {errors}")
        print(f"\nAll files saved to: {MEDIA_DIR}")
        print(f"Metadata saved to: {metadata_file.name}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

