#!/usr/bin/env python3
import os
import sys

# Ensure virtual environment packages are available when running script directly
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
if os.path.isdir(venv_path) and venv_path not in sys.path:
    sys.path.insert(0, venv_path)
import requests
import subprocess
import shutil
import time
from bridge import get_recent_posts, apply_news_template, create_default_bg

SOURCE_CHANNEL = "tedsxh"

def download_image(url, save_path):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True
    except:
        pass
    return False

def make_compilations():
    print("📡 Fetching recent news from Telegram...")
    # Using 0 as last_id to fetch the most recent batch
    posts = get_recent_posts(SOURCE_CHANNEL, 0)
    
    if not posts:
        print("❌ No posts found.")
        return

    # Define premium tier sources
    HIGH_GRADE_SOURCES = ["BBC News", "Reuters", "Bloomberg", "AP News", "The New York Times", "The Wall Street Journal", "The Guardian"]

    # Filter posts: prefer ones with actual text and only high-grade sources
    valid_posts = []
    for p in reversed(posts):
        pid, text, photo_url, story_url = p
        if not text or "News Update" == text.strip():
            continue
            
        # Check if the text contains any of our high-grade source names
        if not any(source in text for source in HIGH_GRADE_SOURCES):
            continue
            
        valid_posts.append(p)
        if len(valid_posts) == 9:
            break
            
    if len(valid_posts) < 9:
        print(f"⚠️ Only found {len(valid_posts)} valid posts. We need 9 to make 3 compilations.")
        # We will just make as many compilations of 3 as we can
    
    music_path = os.path.join(os.path.dirname(__file__), "chill-fm.mp3")
    
    # Process into groups of 3
    compilation_count = 1
    for i in range(0, len(valid_posts), 3):
        group = valid_posts[i:i+3]
        if len(group) < 3:
            break # Need exactly 3 for a compilation
            
        print(f"\n🎬 Creating Compilation #{compilation_count}...")
        
        # Temp dir for this compilation's images
        temp_dir = f"comp_temp_{compilation_count}"
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            for idx, post in enumerate(group):
                pid, text, photo_url, story_url = post
                print(f"  - Processing post {pid} (Part {idx+1}/3)")
                
                raw_img_path = os.path.join(temp_dir, f"raw_{idx+1}.jpg")
                if photo_url and download_image(photo_url, raw_img_path):
                    pass
                else:
                    create_default_bg(raw_img_path)
                    
                # Apply the news template overlay
                edited_path = apply_news_template(raw_img_path, text)
                
                # Move it to the sequence format required by ffmpeg (e.g., img_1.jpg)
                seq_path = os.path.join(temp_dir, f"img_{idx+1}.jpg")
                shutil.move(edited_path, seq_path)
                
            # Create video using FFmpeg slideshow
            output_video = f"news_compilation_{compilation_count}.mp4"
            print(f"  🎥 Rendering 15-second video: {output_video}...")
            
            cmd = [
                'ffmpeg', '-y', 
                '-framerate', '1/5', # 5 seconds per image
                '-i', os.path.join(temp_dir, 'img_%d.jpg'),
                '-stream_loop', '-1', '-i', music_path,
                '-c:v', 'libx264', '-tune', 'stillimage',
                '-c:a', 'aac', '-b:a', '128k',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
                '-shortest', '-t', '15', output_video
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(output_video):
                print(f"  ✅ Successfully rendered {output_video}")
            else:
                print(f"  ❌ Failed to render {output_video}")
                
        finally:
            # Clean up temp images
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        compilation_count += 1
        if compilation_count > 3:
            break

if __name__ == "__main__":
    make_compilations()
