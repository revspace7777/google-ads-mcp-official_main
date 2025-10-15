#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download all media from Jacksonville Moving and Storage Instagram
Profile: @jacksonvillemovingandstorage
Using instaloader library
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Try to import instaloader
try:
    import instaloader
except ImportError:
    print("Installing instaloader...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "instaloader"], check=True)
    import instaloader

# Configuration
INSTAGRAM_USERNAME = "heathevanmartin"
INSTAGRAM_PASSWORD = "Light&Earth_surr3nder@77"
TARGET_PROFILE = "jacksonvillemovingandstorage"
MEDIA_DIR = Path(__file__).parent.parent / "media"

def main():
    print("=" * 80)
    print("INSTAGRAM MEDIA DOWNLOADER")
    print(f"Profile: @{TARGET_PROFILE}")
    print("=" * 80)
    print()
    
    # Create media directory
    MEDIA_DIR.mkdir(exist_ok=True)
    print(f"Media directory: {MEDIA_DIR}")
    print()
    
    # Create instaloader instance
    L = instaloader.Instaloader(
        dirname_pattern=str(MEDIA_DIR / "{target}"),
        filename_pattern="{date_utc}_UTC_{shortcode}",
        download_videos=True,
        download_video_thumbnails=True,
        download_geotags=True,
        download_comments=True,
        save_metadata=True,
        compress_json=False
    )
    
    # Login
    print(f"Logging in as {INSTAGRAM_USERNAME}...")
    try:
        L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print("Login successful!")
    except Exception as e:
        print(f"Login failed: {e}")
        print("Continuing without login (will only get public posts)...")
    
    print()
    
    # Load profile
    print(f"Loading profile @{TARGET_PROFILE}...")
    try:
        profile = instaloader.Profile.from_username(L.context, TARGET_PROFILE)
        
        print(f"Profile: {profile.full_name}")
        print(f"Posts: {profile.mediacount}")
        print(f"Followers: {profile.followers}")
        print(f"Following: {profile.followees}")
        print()
        
    except Exception as e:
        print(f"Error loading profile: {e}")
        return
    
    # Download all posts
    print("=" * 80)
    print("DOWNLOADING POSTS")
    print("=" * 80)
    print()
    
    post_count = 0
    success_count = 0
    error_count = 0
    
    for post in profile.get_posts():
        post_count += 1
        
        try:
            print(f"[{post_count}] Downloading post {post.shortcode}...")
            print(f"    Date: {post.date_utc}")
            print(f"    Type: {'Video' if post.is_video else 'Image'}")
            print(f"    Likes: {post.likes}")
            
            # Download the post
            L.download_post(post, target=TARGET_PROFILE)
            
            success_count += 1
            print(f"    Downloaded!")
            
        except Exception as e:
            error_count += 1
            print(f"    Error: {e}")
            continue
    
    # Summary
    print()
    print("=" * 80)
    print("DOWNLOAD COMPLETE")
    print("=" * 80)
    print(f"Total posts: {post_count}")
    print(f"Successfully downloaded: {success_count}")
    print(f"Errors: {error_count}")
    print(f"\nAll media saved to: {MEDIA_DIR}")
    print()
    
    # List downloaded files
    all_files = list(MEDIA_DIR.glob('**/*'))
    media_files = [f for f in all_files if f.is_file() and f.suffix in ['.jpg', '.mp4', '.txt', '.json']]
    
    print(f"Total files downloaded: {len(media_files)}")
    print("\nFile breakdown:")
    print(f"  Images (.jpg): {len([f for f in media_files if f.suffix == '.jpg'])}")
    print(f"  Videos (.mp4): {len([f for f in media_files if f.suffix == '.mp4'])}")
    print(f"  Metadata (.json, .txt): {len([f for f in media_files if f.suffix in ['.json', '.txt']])}")

if __name__ == "__main__":
    main()

