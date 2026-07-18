import os
import sys
# Ensure virtual environment packages are available when running script directly
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
if os.path.isdir(venv_path) and venv_path not in sys.path:
    sys.path.insert(0, venv_path)

import requests
import time
import re
import subprocess
import shutil
import random
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from instagrapi import Client, exceptions

def load_dotenv():
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(dotenv_path):
        print(f"Loading configuration from {dotenv_path}...")
        with open(dotenv_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip("'").strip('"')

load_dotenv()

IG_USERNAME = os.getenv('IG_USERNAME')
IG_PASSWORD = os.getenv('IG_PASSWORD')
IG_PROXY = os.getenv('IG_PROXY')
TG_PROXY = os.getenv('TG_PROXY') or IG_PROXY
IG_SESSIONID = os.getenv('IG_SESSIONID')
SOURCE_CHANNEL_RAW = os.getenv('TG_SOURCE_CHANNEL')
SOURCE_CHANNEL = None
if SOURCE_CHANNEL_RAW:
    cleaned = SOURCE_CHANNEL_RAW.strip().strip("'").strip('"')
    if not cleaned.startswith('@') and not cleaned.startswith('http') and '/' not in cleaned:
        SOURCE_CHANNEL = cleaned
    else:
        SOURCE_CHANNEL = cleaned.lstrip('@').split('/')[-1]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, 'processed_ids.txt')
SESSION_FILE = os.path.join(BASE_DIR, 'ig_session.json')
HEADLINES_FILE = os.path.join(BASE_DIR, 'processed_headlines.txt')

def normalize_headline(headline):
    return re.sub(r'[^a-zA-Z0-9]', '', headline).lower().strip()

def get_processed_headlines():
    if os.path.exists(HEADLINES_FILE):
        try:
            return set(x.strip() for x in open(HEADLINES_FILE, encoding='utf-8') if x.strip())
        except: pass
    return set()

def add_processed_headline(normalized_hl):
    try:
        with open(HEADLINES_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{normalized_hl}\n")
    except: pass
HIGH_GRADE_SOURCES = ["BBC News", "Reuters", "Bloomberg", "AP News", "The New York Times", "The Wall Street Journal", "The Guardian"]

class InstagramUploader:
    def __init__(self, username, password, session_id, session_file):
        self.username = username
        self.password = password
        self.session_id = session_id
        self.session_file = os.path.join(BASE_DIR, session_file)
        self.client = None
        self.tried_challenge_codes = set()

    def challenge_code_handler(self, username, choice):
        import sys
        import time
        import os
        
        # Interactive Mode
        if sys.stdin.isatty():
            code = input(f"Enter challenge code for {username}: ")
            if not code.isdigit() or len(code) < 6:
                print("Invalid code format.")
                return ""
            if code in self.tried_challenge_codes:
                print("Code already tried.")
                return ""
            self.tried_challenge_codes.add(code)
            return code
            
        # Non-Interactive Environment Polling
        print(f"Waiting for challenge code in environment variables for {username}...")
        
        def reload_env():
            try:
                if 'load_dotenv' in globals():
                    globals()['load_dotenv']()
                else:
                    from bridge import load_dotenv
                    load_dotenv()
            except:
                pass
                
        def check_env():
            code = None
            if username == "neon.bulletin":
                code = os.environ.get('IG_CHALLENGE_CODE_STANDARD')
            elif username == "samar.root":
                code = os.environ.get('IG_CHALLENGE_CODE_TECH')
            if not code:
                code = os.environ.get('IG_CHALLENGE_CODE')
            return code

        reload_env()
        for _ in range(18):
            code = check_env()
            if code and code not in self.tried_challenge_codes:
                self.tried_challenge_codes.add(code)
                return code
            time.sleep(1)
            reload_env()
            
        return ""

    def get_client(self):
        if self.client is not None:
            return self.client
            
        desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
        if os.path.exists(self.session_file):
            try:
                temp_client = Client()
                temp_client.user_agent = desktop_ua
                temp_client.challenge_code_handler = self.challenge_code_handler
                if IG_PROXY:
                    temp_client.set_proxy(IG_PROXY)
                temp_client.load_settings(self.session_file)
                # Bypass user_info_by_username to avoid 429 rate limit hanging
                self.client = temp_client
                return self.client
            except Exception as load_err:
                print(f"Failed to load saved session for {self.username}: {load_err}.")
                try: os.remove(self.session_file)
                except: pass

        self.client = Client()
        self.client.user_agent = desktop_ua
        self.client.challenge_code_handler = self.challenge_code_handler
        
        if IG_PROXY:
            self.client.set_proxy(IG_PROXY)
            
        if self.session_id:
            try:
                self.client.login_by_sessionid(self.session_id)
                self.client.dump_settings(self.session_file)
                return self.client
            except Exception as e:
                print(f"Session ID injection failed: {e}.")

        if not self.password:
            return None

        try:
            self.client.login(self.username, self.password)
            self.client.dump_settings(self.session_file)
            return self.client
        except Exception as e:
            print(f"Instagram login failed for {self.username}: {e}")
            self.client = None
            return None

    def post_reel(self, message, video_path, img_path):
        client = self.get_client()
        if not client: return None
        print(f"  📝 Caption prepared ({len(message)} chars):\n{'-'*30}\n{message}\n{'-'*30}")
        print(f"  ⬆️ Uploading Reel to @{self.username}...")
        for attempt in range(1, 4):
            try:
                media = client.clip_upload(video_path, message, thumbnail=img_path)
                print(f"  🎉 Successfully uploaded Reel to @{self.username}! Media ID: {media.pk}")
                return media
            except Exception as e_upload:
                err_str = str(e_upload).lower()
                print(f"  ⚠️ Upload attempt {attempt} failed for @{self.username}: {e_upload}")
                if "login_required" in err_str:
                    print(f"  🔄 Session invalid! Relogging in for @{self.username}...")
                    self.client = None
                    try: os.remove(self.session_file)
                    except: pass
                    client = self.get_client()
                    if not client: return None
                elif attempt < 3: 
                    import time
                    time.sleep(2 ** attempt)
        print(f"  ❌ All upload attempts failed for @{self.username}.")
        return None

def get_processed_ids():
    if os.path.exists(STATE_FILE):
        try:
            return set(int(x.strip()) for x in open(STATE_FILE) if x.strip())
        except: pass
    return set()

def add_processed_ids(pids):
    with open(STATE_FILE, 'a') as f:
        for pid in pids:
            f.write(f"{pid}\n")

def get_font(size=24):
    font_paths = [
        # Android / Termux native fonts
        "/system/fonts/Roboto-Bold.ttf",
        "/system/fonts/Roboto-Regular.ttf",
        "/system/fonts/DroidSans-Bold.ttf",
        # Linux standard fonts
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def create_default_bg(output_path="default_bg.jpg"):
    w, h = 1080, 1920
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r, g, b = int(15 + (y/h)*20), int(25 + (y/h)*30), int(45 + (y/h)*50)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    img.save(output_path, quality=95)
    img.close()
    return output_path
   # Image Compositing Template
def apply_news_template(image_path, text, account_username="samar.root", is_carousel=False):
    try:
        print(f"  🎨 Applying graphical template to {image_path} for @{account_username}...")
        with Image.open(image_path) as original_img:
            original_img = ImageOps.exif_transpose(original_img).convert('RGBA')
        w_orig, h_orig = original_img.size
        target_w, target_h = 1080, 1920
        img_ratio = w_orig / h_orig
        target_ratio = target_w / target_h
        
        if img_ratio > target_ratio:
            bg_h = target_h
            bg_w = int(bg_h * img_ratio)
        else:
            bg_w = target_w
            bg_h = int(bg_w / img_ratio)
            
        bg_img = original_img.resize((bg_w, bg_h), Image.LANCZOS)
        bg_left = (bg_w - target_w) / 2
        bg_top = (bg_h - target_h) / 2
        bg_right = (bg_w + target_w) / 2
        bg_bottom = (bg_h + target_h) / 2
        bg_img = bg_img.crop((bg_left, bg_top, bg_right, bg_bottom))
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(45))
        
        canvas = bg_img.copy()
        draw = ImageDraw.Draw(canvas)
        overlay = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 130))
        canvas.alpha_composite(overlay)
        
        if img_ratio >= target_ratio:
            sharp_w = target_w
            sharp_h = int(sharp_w / img_ratio)
            paste_x = 0
            paste_y = int(120 + (1100 - sharp_h) / 2)
        else:
            sharp_h = 1100
            sharp_w = int(sharp_h * img_ratio)
            paste_x = int((target_w - sharp_w) / 2)
            paste_y = 120
            
        sharp_img = original_img.resize((sharp_w, sharp_h), Image.LANCZOS)
        border_layer = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border_layer)
        if paste_x == 0:
            border_draw.line([(0, paste_y - 2), (target_w, paste_y - 2)], fill=(255, 255, 255, 140), width=2)
            border_draw.line([(0, paste_y + sharp_h + 1), (target_w, paste_y + sharp_h + 1)], fill=(255, 255, 255, 140), width=2)
        else:
            border_draw.rectangle([paste_x - 2, paste_y - 2, paste_x + sharp_w + 2, paste_y + sharp_h + 2], outline=(255, 255, 255, 180), width=2)
            
        canvas.alpha_composite(border_layer)
        canvas.alpha_composite(sharp_img, dest=(paste_x, paste_y))
        
        source_match = re.search(r'(?i)(source:\s*[^\n]+)', text)
        source_text = ""
        if source_match:
            source_text = source_match.group(1).strip()
            source_text = re.sub(r'[\U00010000-\U0010ffff]', '', source_text)
            source_text = " ".join(source_text.split()).strip()
            
        headline_base = text
        if source_match: headline_base = headline_base.replace(source_match.group(1), "")
        headline_base = re.sub(r'(?i)read\s+full(\s+story)?', '', headline_base)
        headline_base = re.sub(r'(?i)related:\s*join.*', '', headline_base)
        headline_base = " ".join(w for w in headline_base.split() if not w.startswith("http") and not w.startswith("@"))
        clean_headline = re.sub(r'[\U00010000-\U0010ffff]', '', headline_base)
        clean_headline = " ".join(clean_headline.split()).strip()
        clean_headline = re.sub(r'(?i)^\s*breaking\s+news\s*', '', clean_headline).strip()
        clean_headline = clean_headline[:180] or "News Update"
        
        RED = (186, 12, 47, 255)
        BLUE = (12, 47, 186, 255)
        GREEN = (47, 186, 12, 255)
        
        if "tech" in account_username:
            banner_color = BLUE
            banner_title = "TECH NEWS"
        elif "global" in account_username:
            banner_color = GREEN
            banner_title = "GLOBAL NEWS"
        else:
            banner_color = RED
            banner_title = "BREAKING NEWS"
            
        draw.rectangle([40, 1270, 360, 1325], fill=banner_color)
        draw.text((65, 1280), banner_title, fill=(255, 255, 255, 255), font=get_font(30))
        
        font_hl = get_font(40)
        lines, cur = [], []
        for word in clean_headline.split():
            test = " ".join(cur + [word])
            try: tw = draw.textlength(test, font=font_hl)
            except: tw = len(test) * 22
            if tw <= (target_w - 90): cur.append(word)
            else:
                if cur: lines.append(" ".join(cur))
                cur = [word]
        if cur: lines.append(" ".join(cur))
        final = "\n".join(lines[:3])
        
        ty = 1355
        draw.text((42, ty + 2), final, fill=(0, 0, 0, 180), font=font_hl)
        draw.text((40, ty), final, fill=(255, 255, 255, 255), font=font_hl)
        
        if source_text:
            draw.text((40, 1820), source_text, fill=(200, 200, 200, 220), font=get_font(24))
            
        # Draw a clean CTA box at the bottom of the Reel
        if "tech" in account_username:
            cta_text = f"👉 Follow @{account_username} for Tech Updates"
        elif "global" in account_username:
            cta_text = f"👉 Follow @{account_username} for World News"
        else:
            cta_text = f"👉 Follow @{account_username} for Daily News"
            
        font_cta = get_font(22)
        try:
            cta_w = draw.textlength(cta_text, font=font_cta)
        except:
            cta_w = len(cta_text) * 12
        cta_x = int((target_w - cta_w) / 2)
        
        draw.rectangle([cta_x - 30, 1680, cta_x + cta_w + 30, 1750], fill=(255, 255, 255, 30), outline=(255, 255, 255, 100), width=1)
        draw.text((cta_x, 1695), cta_text, fill=(255, 255, 255, 230), font=font_cta)
            
        out = f"edited_{os.path.basename(image_path)}"
        canvas.convert('RGB').save(out, 'JPEG', quality=95)
        
        # Explicit cleanup to prevent memory/file descriptor leaks
        bg_img.close()
        overlay.close()
        sharp_img.close()
        border_layer.close()
        canvas.close()
        
        print(f"  ✨ Template applied successfully. Output: {out}")
        return out
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error applying template: {e}")
        return image_path

def create_news_video(image_path, output_path="news_post.mp4", raw_text=""):
    try:
        import re
        from gtts import gTTS
        
        print(f"  🎬 Compiling video with embedded music and TTS...")
        if os.path.exists(output_path): os.remove(output_path)
        music_path = os.path.join(os.path.dirname(__file__), "chill-fm.mp3")
        
        tts_audio = None
        duration = '5'
        
        if raw_text:
            headline_base = raw_text
            source_match = re.search(r'(?i)(source:\s*[^\n]+)', raw_text)
            if source_match: headline_base = headline_base.replace(source_match.group(1), "")
            headline_base = re.sub(r'(?i)read\s+full(\s+story)?', '', headline_base)
            headline_base = re.sub(r'(?i)related:\s*join.*', '', headline_base)
            headline_base = " ".join(w for w in headline_base.split() if not w.startswith("http") and not w.startswith("@"))
            clean_headline = re.sub(r'[\U00010000-\U0010ffff]', '', headline_base)
            clean_headline = " ".join(clean_headline.split()).strip()
            clean_headline = re.sub(r'(?i)^\s*breaking\s+news\s*', '', clean_headline).strip()
            clean_headline = clean_headline[:180] or "News Update"
            
            if clean_headline and clean_headline != "News Update":
                try:
                    print(f"  🎙️ Generating TTS audio for headline...")
                    tts = gTTS(text=clean_headline, lang='en', tld='co.uk')
                    tts_audio = f"tts_temp_{os.path.basename(image_path)}.mp3"
                    tts.save(tts_audio)
                    # Get TTS duration to ensure video is long enough to finish reading
                    dur_out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', tts_audio], text=True).strip()
                    if dur_out:
                        tts_dur = float(dur_out)
                        if tts_dur > 5.0:
                            duration = str(int(tts_dur) + 1)
                except Exception as e:
                    print(f"TTS generation failed: {e}")
                    tts_audio = None

        if tts_audio:
            zoomd = int(float(duration) * 25)
            cmd = [
                'ffmpeg', '-y', '-loop', '1', '-i', image_path,
                '-stream_loop', '-1', '-i', music_path,
                '-i', tts_audio,
                '-filter_complex', f"[1:a]volume=0.2[bg];[2:a]volume=1.8[voice];[bg][voice]amix=inputs=2:duration=first:dropout_transition=2",
                '-c:v', 'libx264', '-preset', 'ultrafast', '-threads', '4', '-tune', 'stillimage',
                '-c:a', 'aac', '-b:a', '128k', '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1080:1920,format=yuv420p',
                '-t', duration, output_path
            ]
        else:
            cmd = [
                'ffmpeg', '-y', '-loop', '1', '-i', image_path,
                '-stream_loop', '-1', '-i', music_path,
                '-c:v', 'libx264', '-preset', 'ultrafast', '-threads', '4', '-tune', 'stillimage',
                '-c:a', 'aac', '-b:a', '128k', '-pix_fmt', 'yuv420p',
                '-vf', "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                '-shortest', '-t', '5', output_path
            ]
        print(f"  🎥 Running FFmpeg to render video...")
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  ✅ Video rendered successfully. Output: {output_path}")
        
        if tts_audio:
            try: os.remove(tts_audio)
            except: pass
            
        return output_path if r.returncode == 0 else None
    except Exception as e:
        print(f"Error creating video: {e}")
        return None

def post_to_instagram(message, video_path, img_path, account_key="main"):
    env_suffix = ""
    if account_key == "tech": env_suffix = "_TECH"
    elif account_key == "global": env_suffix = "_GLOBAL"
    
    username = os.getenv(f'IG_USERNAME{env_suffix}')
    password = os.getenv(f'IG_PASSWORD{env_suffix}')
    session_id = os.getenv(f'IG_SESSIONID{env_suffix}')
    
    # Map 'main' to 'standard' for session file naming as per tests
    if account_key == "main": account_key = "standard"
    session_file = f'ig_session_{account_key}.json'
    
    if not username:
        print(f"Account {account_key} not configured. Skipping.")
        return None
        
    uploader = InstagramUploader(username, password, session_id, session_file)
    return uploader.post_reel(message, video_path, img_path)

def clean_and_format_caption(text, desc_text="", story_url=None, account_key="main"):
    if account_key == "tech":
        intro_text = "💻 Samar Tech Updates | @the.samar.tech"
        follow_text = "@the.samar.tech"
        tags = "#tech #ai #startups #innovation #technology #gadgets #cybersecurity #thesamartech"
    elif account_key == "global":
        intro_text = "🌍 Samar Global News | @the.samar.global"
        follow_text = "@the.samar.global"
        tags = "#worldnews #finance #economy #globalmarkets #geopolitics #international #thesamarglobal"
    else:
        intro_text = "🏛️ Samar Root Politics & News | @samar.root"
        follow_text = "@samar.root"
        tags = "#politics #breakingnews #currentaffairs #journalism #trending #newsupdate #samarroot"

    if not text: return f"{intro_text}\n\n{tags}"
    
    lines = text.split('\n')
    cleaned = [f"{intro_text}\n"]
    for line in lines:
        if "READ FULL STORY" in line or "teds mordare" in line.lower(): continue
        line = " ".join([w for w in line.split() if not w.startswith("http")])
        if line.strip(): cleaned.append(line.strip())
        
    if desc_text:
        cleaned.append(f"\n{desc_text}")
        
    raw_caption = re.sub(r'\n{3,}', '\n\n', "\n".join(cleaned)).strip()
    if story_url: raw_caption += f"\n\n🔗 FULL STORY LINK:\n👉 {story_url}"
    raw_caption += f"\n\n🚨 WHAT DO YOU THINK? Drop your thoughts below! 👇\n📌 SAVE this post to stay updated.\n🔔 Follow {follow_text} for breaking news!\n\n{tags}"
    return raw_caption



def process_individual(post, account_key="main"):
    pid, text, desc_text, photo_url, story_url = post[:5]
    print(f"  ⏭ Processing individual low-grade post #{pid} for {account_key}...")
    img_path = f"temp_{pid}.jpg"
    try:
        if photo_url:
            print(f"  📥 Downloading article image from RSS feed...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                r = requests.get(photo_url, headers=headers, timeout=15)
                if r.status_code == 200:
                    with open(img_path, 'wb') as f: f.write(r.content)
                else:
                    print(f"  ⚠️ Image download failed with status {r.status_code}")
            except Exception as e: 
                print(f"  ⚠️ Image download exception: {e}")
        if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
            print(f"  ⚠️ No image found, generating default background.")
            create_default_bg(img_path)
            
        env_suffix = ""
        if account_key == "tech": env_suffix = "_TECH"
        elif account_key == "global": env_suffix = "_GLOBAL"
        target_username = os.getenv(f'IG_USERNAME{env_suffix}', 'neon.bulletin')
            
        edited = apply_news_template(img_path, text, account_username=target_username)
        video = create_news_video(edited, f"news_video_{pid}.mp4", text)
        
        if video:
            print(f"  ✍️ Formatting caption and tags...")
            cap = clean_and_format_caption(text, desc_text=desc_text, story_url=story_url, account_key=account_key)
            print(f"  🚀 Starting Instagram upload for {account_key}...")
            res = post_to_instagram(cap, video, edited, account_key=account_key)
            return res is not None
        return False
    finally:
        for fp in [f"edited_{os.path.basename(img_path)}", f"news_video_{pid}.mp4", img_path]:
            if os.path.exists(fp) and fp != "default_bg.jpg":
                try: os.remove(fp)
                except: pass

def get_recent_posts(source, processed_ids, limit=200):
    import xml.etree.ElementTree as ET
    import hashlib
    import concurrent.futures
    
    feeds = [
        "http://feeds.bbci.co.uk/news/rss.xml",
        "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://techcrunch.com/feed/"
    ]
    
    all_posts = []
    print(f"  📡 Starting to fetch up to {limit} posts from {len(feeds)} direct RSS feeds concurrently...")
    
    def fetch_feed(feed_url):
        feed_posts = []
        print(f"    📄 Fetching feed: {feed_url}...")
        try:
            r = requests.get(feed_url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            if r.status_code == 200:
                xml_text = re.sub(r'\sxmlns="[^"]+"', '', r.text)
                root = ET.fromstring(xml_text)
                for item in root.findall('.//item'):
                    title = item.find('title')
                    link = item.find('link')
                    description = item.find('description')
                    
                    if title is None or link is None: continue
                    text = title.text.strip()
                    story_url = link.text.strip()
                    pid = int(hashlib.md5(story_url.encode()).hexdigest(), 16) % (10**9)
                    
                    if pid in processed_ids: continue
                    
                    photo_url = None
                    media_content = item.find('.//{http://search.yahoo.com/mrss/}content')
                    if media_content is not None and 'url' in media_content.attrib:
                        photo_url = media_content.attrib['url']
                    else:
                        media_thumb = item.find('.//{http://search.yahoo.com/mrss/}thumbnail')
                        if media_thumb is not None and 'url' in media_thumb.attrib:
                            photo_url = media_thumb.attrib['url']
                            
                    desc_text = ""
                    if description is not None and description.text:
                        img_match = re.search(r'<img[^>]+src=["\'](.*?)["\']', description.text)
                        if not photo_url and img_match: photo_url = img_match.group(1)
                        desc_text = re.sub(r'<[^>]+>', '', description.text).strip()
                            
                    if len(text.split()) < 4 and not desc_text: continue
                    feed_posts.append((pid, text, desc_text, photo_url, story_url))
                    if len(feed_posts) >= limit: break
            else:
                print(f"  ⚠️ Feed {feed_url} returned HTTP {r.status_code}")
        except Exception as e:
            print(f"  ❌ Error fetching {feed_url}: {e}")
        return feed_posts

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(fetch_feed, feeds)
        for posts in results:
            all_posts.extend(posts)
            if len(all_posts) >= limit:
                all_posts = all_posts[:limit]
                break
            
    # Sort by ID (arbitrary but consistent)
    return sorted(all_posts, key=lambda x: x[0])

def main():
    if not IG_USERNAME or not IG_PASSWORD or not SOURCE_CHANNEL:
        print("❌ Missing config in .env.")
        return
        
    print(f"\n{'='*55}\n  📡 Bridge active — Dual-Mode Pipeline\n{'='*55}\n")
    
    # Run once at startup to create a dummy processed_ids if migrating from last_msg_id
    if not os.path.exists(STATE_FILE) and os.path.exists('last_msg_id.txt'):
        try:
            lid = int(open('last_msg_id.txt').read().strip())
            add_processed_ids(range(1, lid + 1))
        except: pass

    processed_hl = get_processed_headlines()
    processed_ids = get_processed_ids()
    posts_today = {"main": 0, "tech": 0, "global": 0}
    next_ready = {"main": 0, "tech": 0, "global": 0}
    last_reset_day = datetime.now(timezone.utc).day

    while True:
        try:
            print(f"\n🔄 Polling RSS Feeds for new posts...")
            current_day = datetime.now(timezone.utc).day
            if current_day != last_reset_day:
                posts_today = {"main": 0, "tech": 0, "global": 0}
                last_reset_day = current_day
                
            # Fetch a deep history (up to 200 posts) so no high-grade news is missed
            all_recent = get_recent_posts(SOURCE_CHANNEL, processed_ids, limit=200)
            print(f"🔍 Checking {len(all_recent)} recent posts for duplicate headlines...")
            
            # Filter specifically for unprocessed unique headlines
            new_posts = []
            for p in all_recent:
                # Clean headline using exact same logic as apply_news_template
                source_match = re.search(r'(?i)(source:\s*[^\n]+)', p[1])
                headline_base = p[1]
                if source_match: headline_base = headline_base.replace(source_match.group(1), "")
                headline_base = re.sub(r'(?i)read\s+full(\s+story)?', '', headline_base)
                headline_base = re.sub(r'(?i)related:\s*join.*', '', headline_base)
                headline_base = " ".join(w for w in headline_base.split() if not w.startswith("http") and not w.startswith("@"))
                clean_hl = re.sub(r'[\U00010000-\U0010ffff]', '', headline_base)
                clean_hl = " ".join(clean_hl.split()).strip()
                clean_hl = re.sub(r'(?i)^\s*breaking\s+news\s*', '', clean_hl).strip()
                clean_hl = clean_hl[:180] or "News Update"
                
                norm_hl = normalize_headline(clean_hl)
                if norm_hl in processed_hl:
                    # Already posted this headline, mark message ID as processed
                    add_processed_ids([p[0]])
                    continue
                new_posts.append((p[0], p[1], p[2], p[3], p[4], norm_hl))
            
            if new_posts:
                print(f"\n📬 Found {len(new_posts)} unprocessed post(s). Routing...")
                now = time.time()
                
                # Implement Strategy B: Category Routing
                for p in new_posts:
                    text_lower = p[1].lower()
                    
                    # Routing logic based on keywords or sources
                    if any(kw in text_lower for kw in ["tech", "ai", "apple", "google", "startup", "crypto", "gadget", "software", "cyber"]):
                        target_account = "tech"
                    elif any(kw in text_lower for kw in ["global", "world", "market", "finance", "war", "economy", "reuters", "bloomberg", "international"]):
                        target_account = "global"
                    else:
                        target_account = "main" # main handles politics and general news
                        
                    quota = 50 if target_account == "main" else 30
                    if posts_today[target_account] >= quota:
                        # Try fallback if main is full
                        if target_account == "main" and posts_today["global"] < 30:
                            target_account = "global"
                        else:
                            continue
                            
                    # Check if this account is currently on cooldown
                    if next_ready[target_account] > now:
                        continue # Skip this post for now, it will be picked up next poll
                            
                    # Double check we haven't already processed it just in case
                    if p[0] in processed_ids: continue
                    if p[5] in processed_hl:
                        add_processed_ids([p[0]])
                        processed_ids.add(p[0])
                        continue
                    
                    print(f"  ⏭ Routing post #{p[0]} to [{target_account.upper()}] account...")
                    success = process_individual(p, account_key=target_account)
                    if success:
                        add_processed_ids([p[0]])
                        processed_ids.add(p[0])
                        add_processed_headline(p[5])
                        processed_hl.add(p[5])
                        posts_today[target_account] += 1
                        print(f"  ✅ Uploaded post #{p[0]}. ({posts_today[target_account]}/{quota} today for {target_account})")
                        
                        wait_time = random.randint(180, 300) if target_account == "main" else random.randint(240, 420)
                        print(f"  ⏳ Setting [{target_account.upper()}] cooldown for {wait_time // 60}m {wait_time % 60}s...")
                        next_ready[target_account] = time.time() + wait_time
                        now = time.time()
                    else:
                        print(f"  ❌ Post #{p[0]} failed. Pausing this account.")
                        next_ready[target_account] = time.time() + 300 # 5 min penalty
                        now = time.time()
                    
        except Exception as e:
            print(f"Polling error: {e}")
            
        print(f"💤 Polling sleep: Waiting 60s for next check...")
        time.sleep(60)

if __name__ == "__main__":
    main()
