#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download all media from Jacksonville Moving and Storage Instagram
Profile: @jacksonvillemovingandstorage
URL: https://www.instagram.com/jacksonvillemovingandstorage/
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

# Try to import playwright
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Installing playwright...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.async_api import async_playwright

# Configuration
INSTAGRAM_USERNAME = "heathevanmartin"
INSTAGRAM_PASSWORD = "Light&Earth_surr3nder@77"
TARGET_PROFILE = "jacksonvillemovingandstorage"
MEDIA_DIR = Path(__file__).parent.parent / "media"

def random_delay(min_ms=1000, max_ms=3000):
    """Human-like random delay"""
    delay = random.uniform(min_ms / 1000, max_ms / 1000)
    time.sleep(delay)

async def login_to_instagram(page):
    """Login to Instagram with stealth"""
    print("Logging in to Instagram...")
    
    # Navigate to Instagram
    await page.goto('https://www.instagram.com/', wait_until='domcontentloaded', timeout=60000)
    await asyncio.sleep(random.uniform(3, 5))
    
    # Fill username
    await page.fill('input[name="username"]', INSTAGRAM_USERNAME)
    await asyncio.sleep(random.uniform(0.5, 1))
    
    # Fill password
    await page.fill('input[name="password"]', INSTAGRAM_PASSWORD)
    await asyncio.sleep(random.uniform(0.8, 1.5))
    
    # Click login
    await page.click('button[type="submit"]')
    await asyncio.sleep(random.uniform(4, 6))
    
    # Handle "Save login info" dialog if it appears
    try:
        not_now_button = await page.wait_for_selector('button:has-text("Not now")', timeout=5000)
        if not_now_button:
            await not_now_button.click()
            await asyncio.sleep(random.uniform(1, 2))
    except:
        pass
    
    # Handle notifications dialog
    try:
        not_now_button = await page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
        if not_now_button:
            await not_now_button.click()
            await asyncio.sleep(random.uniform(1, 2))
    except:
        pass
    
    print("Login successful!")

async def get_all_post_urls(page, profile_username):
    """Get all post URLs from profile"""
    print(f"Navigating to @{profile_username}...")
    
    await page.goto(f'https://www.instagram.com/{profile_username}/', wait_until='domcontentloaded', timeout=60000)
    await asyncio.sleep(random.uniform(5, 7))
    
    # Get post count
    try:
        post_count_text = await page.locator('li:has-text("posts")').first.text_content()
        post_count = int(''.join(filter(str.isdigit, post_count_text.split()[0].replace(',', ''))))
        print(f"Found {post_count} posts on profile")
    except:
        print("Could not determine post count, continuing anyway...")
        post_count = None
    
    # Scroll to load all posts
    print("Scrolling to load all posts...")
    post_links = set()
    
    last_count = 0
    stall_count = 0
    
    while stall_count < 3:
        # Get all post links currently visible
        links = await page.locator('a[href*="/p/"]').all()
        
        for link in links:
            href = await link.get_attribute('href')
            if href:
                post_links.add('https://www.instagram.com' + href if href.startswith('/') else href)
        
        # Scroll down
        await page.evaluate('window.scrollBy(0, window.innerHeight)')
        await asyncio.sleep(random.uniform(1.5, 2.5))
        
        # Check if we got new links
        if len(post_links) == last_count:
            stall_count += 1
        else:
            stall_count = 0
            last_count = len(post_links)
        
        print(f"Loaded {len(post_links)} post URLs... (stall count: {stall_count}/3)")
    
    print(f"Total posts found: {len(post_links)}")
    return list(post_links)

async def download_media_from_post(page, post_url, media_dir, index):
    """Download all media (images/videos) from a single post"""
    print(f"\n[{index}] Processing: {post_url}")
    
    await page.goto(post_url, wait_until='domcontentloaded', timeout=45000)
    await asyncio.sleep(random.uniform(3, 4))
    
    media_files = []
    
    # Get all images
    images = await page.locator('article img').all()
    for img_idx, img in enumerate(images):
        try:
            src = await img.get_attribute('src')
            if src and 'instagram' in src:
                # Download image
                response = requests.get(src)
                if response.status_code == 200:
                    filename = f"post_{index}_img_{img_idx}.jpg"
                    filepath = media_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    media_files.append(filename)
                    print(f"  Downloaded: {filename}")
        except Exception as e:
            print(f"  Error downloading image {img_idx}: {e}")
    
    # Get all videos
    videos = await page.locator('article video').all()
    for vid_idx, video in enumerate(videos):
        try:
            src = await video.get_attribute('src')
            if src:
                # Download video
                response = requests.get(src)
                if response.status_code == 200:
                    filename = f"post_{index}_video_{vid_idx}.mp4"
                    filepath = media_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    media_files.append(filename)
                    print(f"  Downloaded: {filename}")
        except Exception as e:
            print(f"  Error downloading video {vid_idx}: {e}")
    
    # Get post caption/text
    try:
        caption_elem = await page.locator('article h1').first
        caption = await caption_elem.text_content() if caption_elem else None
    except:
        caption = None
    
    return {
        'post_url': post_url,
        'index': index,
        'media_files': media_files,
        'caption': caption,
        'downloaded_at': datetime.now().isoformat()
    }

async def main():
    print("=" * 80)
    print("INSTAGRAM MEDIA DOWNLOADER")
    print("Jacksonville Moving and Storage (@jacksonvillemovingandstorage)")
    print("=" * 80)
    print()
    
    # Create media directory
    MEDIA_DIR.mkdir(exist_ok=True)
    print(f"Media directory: {MEDIA_DIR}")
    print()
    
    async with async_playwright() as p:
        # Launch browser with stealth
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Create context with realistic settings
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        # Stealth JavaScript
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        page = await context.new_page()
        
        # Login
        await login_to_instagram(page)
        
        # Get all post URLs
        post_urls = await get_all_post_urls(page, TARGET_PROFILE)
        
        # Download media from each post
        print("\n" + "=" * 80)
        print("DOWNLOADING MEDIA")
        print("=" * 80)
        
        all_downloads = []
        
        for idx, post_url in enumerate(post_urls, 1):
            try:
                result = await download_media_from_post(page, post_url, MEDIA_DIR, idx)
                all_downloads.append(result)
                
                # Save progress
                progress_file = MEDIA_DIR / 'download_progress.json'
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(all_downloads, f, indent=2, ensure_ascii=False)
                
            except Exception as e:
                print(f"  Error processing post {idx}: {e}")
                continue
        
        # Summary
        print("\n" + "=" * 80)
        print("DOWNLOAD COMPLETE")
        print("=" * 80)
        print(f"Posts processed: {len(all_downloads)}")
        total_files = sum(len(d['media_files']) for d in all_downloads)
        print(f"Total files downloaded: {total_files}")
        print(f"Saved to: {MEDIA_DIR}")
        
        # Save metadata
        metadata_file = MEDIA_DIR / 'instagram_download_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'profile': TARGET_PROFILE,
                'download_date': datetime.now().isoformat(),
                'total_posts': len(all_downloads),
                'total_files': total_files,
                'posts': all_downloads
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nMetadata saved to: {metadata_file.name}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

