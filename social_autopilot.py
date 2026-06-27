import os
import sys
import time
import requests
import re
from datetime import datetime
from instagrapi import Client

# Load environment
def load_dotenv():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        with open(dotenv_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip("'").strip('"')

load_dotenv()

# Config
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
LINKEDIN_PERSON_URN = os.getenv('LINKEDIN_PERSON_URN') # e.g. urn:li:person:abcdef

IG_BUSINESS_USERNAME = os.getenv('IG_BUSINESS_USERNAME')
IG_BUSINESS_PASSWORD = os.getenv('IG_BUSINESS_PASSWORD')
IG_BUSINESS_SESSION_FILE = 'ig_business_session.json'

GITHUB_REPO = os.getenv('GITHUB_REPO') # e.g. owner/repo
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

STATE_FILE = 'autopilot_processed_commits.txt'

def log(msg, level="INFO"):
    print(f"[{datetime.now().isoformat()}] [{level}] [Autopilot] {msg}")
    sys.stdout.flush()

def get_processed_commits():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def add_processed_commit(sha):
    with open(STATE_FILE, 'a') as f:
        f.write(f"{sha}\n")

# LinkedIn Publishing
def post_to_linkedin(text):
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
        log("LinkedIn credentials not set. Skipping.", "WARNING")
        return False
    
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = {
        "author": LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code in (200, 201):
            log("Successfully posted update to LinkedIn!")
            return True
        else:
            log(f"Failed to post to LinkedIn: {response.status_code} - {response.text}", "ERROR")
            return False
    except Exception as e:
        log(f"LinkedIn posting error: {e}", "ERROR")
        return False

# Business Instagram Publishing
def post_to_business_instagram(text):
    if not IG_BUSINESS_USERNAME or not IG_BUSINESS_PASSWORD:
        log("Instagram Business credentials not set. Skipping.", "WARNING")
        return False

    client = Client()
    if os.path.exists(IG_BUSINESS_SESSION_FILE):
        try:
            client.load_settings(IG_BUSINESS_SESSION_FILE)
            client.account_info()
            log("Loaded existing Instagram Business session.")
        except Exception:
            log("Saved Instagram Business session invalid. Performing fresh login...")
            try: os.remove(IG_BUSINESS_SESSION_FILE)
            except: pass
            
    if not client.user_id:
        try:
            client.login(IG_BUSINESS_USERNAME, IG_BUSINESS_PASSWORD)
            client.dump_settings(IG_BUSINESS_SESSION_FILE)
            log("Instagram Business login successful!")
        except Exception as e:
            log(f"Instagram Business login failed: {e}", "ERROR")
            return False

    try:
        # Business Instagram standard posting (Text-only or simple placeholder image)
        # Note: Instagram requires a media attachment, so we generate a simple image dynamically
        from PIL import Image, ImageDraw, ImageFont
        import os
        def get_font(size=40):
            font_paths = [
                "/system/fonts/Roboto-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
            ]
            for p in font_paths:
                if os.path.exists(p): return ImageFont.truetype(p, size)
            return ImageFont.load_default()
            
        img = Image.new('RGB', (1080, 1080), color=(15, 23, 42)) # Sleek dark blue/gray
        d = ImageDraw.Draw(img)
        
        # Write title/snippet
        title = "TECHNICAL UPDATE"
        d.text((50, 50), title, fill=(168, 85, 247), font=get_font(60)) # Purple accent
        
        wrapped_text = text[:300] + "..." if len(text) > 300 else text
        
        # Add very basic text wrapping for long lines
        lines, cur_line = [], []
        for word in wrapped_text.split():
            cur_line.append(word)
            if len(" ".join(cur_line)) > 45: # approx chars per line at size 40
                lines.append(" ".join(cur_line[:-1]))
                cur_line = [word]
        if cur_line: lines.append(" ".join(cur_line))
        wrapped_text = "\n".join(lines)
        
        d.text((50, 150), wrapped_text, fill=(255, 255, 255), font=get_font(40))
        
        temp_img_path = "temp_business_post.jpg"
        img.save(temp_img_path)
        
        media = client.photo_upload(temp_img_path, caption=text)
        log(f"Successfully posted to Business Instagram! ID: {media.id}")
        
        try: os.remove(temp_img_path)
        except: pass
        return True
    except Exception as e:
        log(f"Instagram Business posting error: {e}", "ERROR")
        return False

# GitHub Commit Monitoring
def check_github_commits():
    if not GITHUB_REPO:
        log("GITHUB_REPO not configured in .env", "WARNING")
        return
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/commits"
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            log(f"Failed to fetch commits: {r.status_code} - {r.text}", "ERROR")
            return
            
        commits = r.json()
        processed = get_processed_commits()
        
        # Process from oldest to newest
        for commit in reversed(commits[:5]):
            sha = commit.get("sha")
            if sha in processed: continue
            
            message = commit.get("commit", {}).get("message", "")
            author = commit.get("commit", {}).get("author", {}).get("name", "Developer")
            
            log(f"Found new commit: {sha[:7]} by {author}")
            
            # Format update message
            post_content = (
                f"🚀 GitHub Code Update | {GITHUB_REPO}\n\n"
                f"A new commit was pushed to our repository:\n"
                f"📝 Message: {message}\n"
                f"👤 Author: {author}\n"
                f"🔗 SHA: {sha[:7]}\n\n"
                f"#github #git #devops #cicd #automation #softwareengineering #coding"
            )
            
            # Publish to LinkedIn and Business Instagram
            li_success = post_to_linkedin(post_content)
            ig_success = post_to_business_instagram(post_content)
            
            if li_success or ig_success:
                add_processed_commit(sha)
                
    except Exception as e:
        log(f"GitHub monitoring error: {e}", "ERROR")

def main():
    log("Social Autopilot service started.")
    while True:
        try:
            check_github_commits()
        except Exception as e:
            log(f"Error in autopilot loop: {e}", "ERROR")
        time.sleep(600) # Check every 10 minutes

if __name__ == "__main__":
    main()
