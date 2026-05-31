#!/usr/bin/env python3
import os
import glob

def clean_workspace():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define patterns of junk files that might be left behind on a crash
    junk_patterns = [
        "temp_*.jpg",
        "edited_temp_*.jpg",
        "news_video_*.mp4",
        "edited_default_bg.jpg",
        "test_bg.jpg",
        "test_video.mp4",
        "test_video.mp4.jpg",
        "test_upload.py",
        "test_video_upload.py",
        "*.session",  # Temporary telethon/aiogram sessions not used anymore
    ]
    
    print(f"🧹 Starting workspace cleanup in: {base_dir}")
    removed_count = 0
    
    for pattern in junk_patterns:
        search_path = os.path.join(base_dir, pattern)
        for file_path in glob.glob(search_path):
            try:
                # Protect specific files from ever being deleted accidentally
                if "ig_session.json" in file_path:
                    continue
                    
                os.remove(file_path)
                print(f"  🗑️ Deleted orphaned file: {os.path.basename(file_path)}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {os.path.basename(file_path)}: {e}")
                
    print(f"✨ Cleanup complete! Removed {removed_count} temporary/junk files.")

if __name__ == "__main__":
    clean_workspace()
