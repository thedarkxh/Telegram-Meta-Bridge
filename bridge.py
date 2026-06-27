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
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
HIGH_GRADE_SOURCES = ["BBC News", "Reuters", "Bloomberg", "AP News", "The New York Times", "The Wall Street Journal", "The Guardian"]

ig_client = None

def get_ig_client():
    global ig_client
    if ig_client is not None:
        return ig_client
        
    if os.path.exists(SESSION_FILE):
        try:
            temp_client = Client()
            if IG_PROXY:
                print(f"🌐 Routing Instagram traffic through proxy: {IG_PROXY}")
                temp_client.set_proxy(IG_PROXY)
            temp_client.load_settings(SESSION_FILE)
            temp_client.user_info_by_username(IG_USERNAME)
            print("✅ Loaded existing Instagram session.")
            ig_client = temp_client
            return ig_client
        except Exception as load_err:
            print(f"⚠️ Failed to load saved session: {load_err}. Forcing fresh login.")
            try: os.remove(SESSION_FILE)
            except: pass

    print(f"Logging into Instagram as {IG_USERNAME}...")
    ig_client = Client()
    if IG_PROXY:
        print(f"🌐 Routing Instagram traffic through proxy: {IG_PROXY}")
        ig_client.set_proxy(IG_PROXY)
        
    # Inject trusted browser cookie to bypass IP/Device blacklists completely
    if IG_SESSIONID:
        print("🔑 Injecting trusted Browser Session ID to bypass API blocks...")
        try:
            ig_client.login_by_sessionid(IG_SESSIONID)
            print("✅ Browser session accepted! Logged in successfully.")
            # We don't save this to SESSION_FILE to avoid corrupting the mobile device settings
            return ig_client
        except Exception as e:
            print(f"❌ Session ID injection failed: {e}. Falling back to standard login...")

    try:
        ig_client.login(IG_USERNAME, IG_PASSWORD)
        ig_client.dump_settings(SESSION_FILE)
        print("✅ Instagram login successful! Session saved.")
        return ig_client
    except Exception as e:
        print(f"❌ Instagram login failed: {e}")
        ig_client = None
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
    return output_path

def apply_news_template(image_path, text):
    try:
        original_img = Image.open(image_path).convert('RGBA')
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
        draw.rectangle([40, 1270, 360, 1325], fill=RED)
        draw.text((65, 1280), "BREAKING NEWS", fill=(255, 255, 255, 255), font=get_font(30))
        
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
            
        out = f"edited_{os.path.basename(image_path)}"
        canvas.convert('RGB').save(out, 'JPEG', quality=95)
        return out
    except Exception as e:
        print(f"Error applying template: {e}")
        return image_path

def create_news_video(image_path, output_path="news_post.mp4"):
    try:
        print(f"Compiling 5s video with embedded music...")
        if os.path.exists(output_path): os.remove(output_path)
        music_path = os.path.join(os.path.dirname(__file__), "chill-fm.mp3")
        cmd = [
            'ffmpeg', '-y', '-loop', '1', '-i', image_path,
            '-stream_loop', '-1', '-i', music_path,
            '-c:v', 'libx264', '-tune', 'stillimage',
            '-c:a', 'aac', '-b:a', '128k', '-pix_fmt', 'yuv420p',
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
            '-shortest', '-t', '5', output_path
        ]
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path if r.returncode == 0 else None
    except Exception: return None

def post_to_instagram(message, video_path, img_path):
    global ig_client
    print(f"📤 Uploading video to Instagram...")
    try:
        client = get_ig_client()
        if not client: return None
        for attempt in range(1, 4):
            try:
                media = client.clip_upload(video_path, message, thumbnail=img_path)
                print(f"✅ Posted Reel to Instagram! ID: {media.id}")
                return media
            except Exception as e_upload:
                err_str = str(e_upload).lower()
                print(f"⚠️ Upload attempt {attempt} failed ({e_upload}).")
                if "login_required" in err_str:
                    print("🔄 Session expired mid-upload. Wiping session and forcing re-login...")
                    ig_client = None
                    try: os.remove(SESSION_FILE)
                    except: pass
                    client = get_ig_client()
                    if not client: return None
                elif attempt < 3: 
                    time.sleep(2 ** attempt)
        return None
    except Exception as e:
        print(f"❌ Instagram upload error: {e}")
        return None

def clean_and_format_caption(text, story_url=None):
    if not text: return "Neon Bulletin News Update | @neon.bulletin\n\n#news #breakingnews #globalnews #neonbulletin #worldnews #currentaffairs #explorepage #viral #journalism #trending #internationalnews #dailynews #latestnews #newsupdate"
    lines = text.split('\n')
    cleaned = ["📡 Neon Bulletin News Update | @neon.bulletin 📡\n"]
    for line in lines:
        if "READ FULL STORY" in line or "teds mordare" in line.lower(): continue
        line = " ".join([w for w in line.split() if not w.startswith("http")])
        if line.strip(): cleaned.append(line.strip())
    raw_caption = re.sub(r'\n{3,}', '\n\n', "\n".join(cleaned)).strip()
    if story_url: raw_caption += f"\n\n🔗 FULL STORY LINK:\n👉 {story_url}"
    raw_caption += "\n\n🚨 WHAT DO YOU THINK? Drop your thoughts below! 👇\n📌 SAVE this post to stay updated.\n🔔 Follow @neon.bulletin for breaking news!\n\n#news #breakingnews #globalnews #neonbulletin #worldnews #currentaffairs #explorepage #viral #journalism #trending #internationalnews #dailynews #latestnews #newsupdate"
    return raw_caption

def process_compilation(posts_group):
    # posts_group: list of (pid, text, photo_url, story_url)
    print(f"  🎬 Creating high-grade compilation reel with {len(posts_group)} stories...")
    temp_dir = f"comp_temp_{int(time.time())}"
    os.makedirs(temp_dir, exist_ok=True)
    music_path = os.path.join(os.path.dirname(__file__), "chill-fm.mp3")
    output_video = f"compilation_{posts_group[-1][0]}.mp4"
    
    try:
        for idx, post in enumerate(posts_group):
            pid, text, photo_url, story_url = post
            raw_img = os.path.join(temp_dir, f"raw_{idx+1}.jpg")
            if photo_url:
                try:
                    r = requests.get(photo_url, timeout=15)
                    if r.status_code == 200:
                        with open(raw_img, 'wb') as f: f.write(r.content)
                except: pass
            if not os.path.exists(raw_img) or os.path.getsize(raw_img) == 0:
                create_default_bg(raw_img)
            edited = apply_news_template(raw_img, text)
            shutil.move(edited, os.path.join(temp_dir, f"img_{idx+1}.jpg"))
            
        duration = len(posts_group) * 5
        cmd = [
            'ffmpeg', '-y', '-framerate', '1/5', 
            '-i', os.path.join(temp_dir, 'img_%d.jpg'),
            '-stream_loop', '-1', '-i', music_path,
            '-c:v', 'libx264', '-tune', 'stillimage',
            '-c:a', 'aac', '-b:a', '128k', '-pix_fmt', 'yuv420p',
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
            '-shortest', '-t', str(duration), output_video
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(output_video):
            caption = "🚨 GLOBAL PULSE: Top Breaking Stories You Missed 🌍👇\n\n"
            for i, p in enumerate(posts_group):
                clean = re.sub(r'(?i)read\s+full(\s+story)?', '', p[1])
                clean = re.sub(r'(?i)related:\s*join.*', '', clean)
                clean = re.sub(r'http\S+', '', clean)
                caption += f"{i+1}️⃣ {clean.strip()[:150]}...\n\n"
            caption += "🔗 Read the full deep-dive stories at the link in our bio!\n\n👇 Which of these global shifts will have the biggest impact? Drop your thoughts!\n\n#news #breakingnews #globalnews #neonbulletin #worldnews #currentaffairs #explorepage #viral #journalism #trending #internationalnews #dailynews #latestnews #newsupdate"
            
            thumb = os.path.join(temp_dir, 'img_1.jpg')
            res = post_to_instagram(caption, output_video, thumb)
            return res is not None
        return False
    except Exception as e:
        print(f"Compilation error: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        if os.path.exists(output_video): os.remove(output_video)

def process_individual(post):
    pid, text, photo_url, story_url = post
    print(f"  ⏭ Processing individual low-grade post #{pid}...")
    img_path = f"temp_{pid}.jpg"
    try:
        if photo_url:
            try:
                r = requests.get(photo_url, timeout=15)
                if r.status_code == 200:
                    with open(img_path, 'wb') as f: f.write(r.content)
            except: pass
        if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
            create_default_bg(img_path)
            
        edited = apply_news_template(img_path, text)
        video = create_news_video(edited, f"news_video_{pid}.mp4")
        if video:
            cap = clean_and_format_caption(text, story_url)
            res = post_to_instagram(cap, video, edited)
            return res is not None
        return False
    finally:
        for fp in [f"edited_{os.path.basename(img_path)}", f"news_video_{pid}.mp4", img_path]:
            if os.path.exists(fp) and fp != "default_bg.jpg":
                try: os.remove(fp)
                except: pass

def _fetch_telegram_page(url, proxies, timeout=20):
    """Try fetching a Telegram page with multi-domain fallback and retries."""
    # Extract the path from the URL so we can try alternate domains
    parsed = urlparse(url)
    path = parsed.path
    if parsed.query:
        path += f"?{parsed.query}"
    
    domains = ["t.me", "telegram.me"]
    last_error = None
    
    for domain in domains:
        attempt_url = f"https://{domain}{path}"
        for attempt in range(1, 4):  # 3 retries per domain
            try:
                r = requests.get(attempt_url, timeout=timeout, proxies=proxies, 
                                 headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
                if r.status_code == 200:
                    return r
                elif r.status_code == 429:
                    wait = min(2 ** attempt * 5, 60)
                    print(f"  ⏳ Rate-limited by {domain} (429). Waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"  ⚠️ {domain} returned HTTP {r.status_code}")
                    break  # Try next domain
            except requests.exceptions.ProxyError as e:
                print(f"  ❌ Proxy error connecting to {domain}: {e}")
                last_error = e
                break  # Proxy is broken, no point retrying
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
                last_error = e
                if attempt < 3:
                    wait = 2 ** attempt
                    print(f"  ⚠️ {domain} connection failed (attempt {attempt}/3). Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"  ❌ {domain} unreachable after 3 attempts.")
            except requests.exceptions.RequestException as e:
                last_error = e
                print(f"  ❌ Request error for {domain}: {e}")
                break
    
    # All domains failed — print diagnostic
    if last_error:
        err_name = type(last_error).__name__
        if "Timeout" in err_name or "Connection" in err_name:
            print(f"\n{'='*60}")
            print(f"  🚫 TELEGRAM IS BLOCKED ON THIS NETWORK")
            print(f"  All Telegram domains are unreachable.")
            print(f"  Error: {err_name}")
            print(f"")
            print(f"  FIX: Set TG_PROXY in your .env file:")
            print(f"    TG_PROXY=socks5://your-proxy:port")
            print(f"    TG_PROXY=http://your-proxy:port")
            print(f"{'='*60}\n")
    return None

def get_recent_posts(username, processed_ids, limit=200):
    current_url = f"https://t.me/s/{username}"
    all_posts = []
    pages = 0
    proxies = {"http": TG_PROXY, "https": TG_PROXY} if TG_PROXY else None
    
    if TG_PROXY:
        print(f"🌐 Routing Telegram traffic through proxy: {TG_PROXY}")
    
    consecutive_failures = 0
    max_consecutive_failures = 3
    
    while pages < 10 and len(all_posts) < limit:
        pages += 1
        
        r = _fetch_telegram_page(current_url, proxies)
        if r is None:
            consecutive_failures += 1
            if consecutive_failures >= max_consecutive_failures:
                print(f"  ❌ {max_consecutive_failures} consecutive page failures. Stopping pagination.")
                break
            continue
        
        consecutive_failures = 0  # Reset on success
        html = r.text
            
        blocks = html.split('<div class="tgme_widget_message text_not_supported_wrap js-widget_message"')[1:]
        if not blocks: blocks = html.split('tgme_widget_message ')[1:]
        if not blocks: break
        
        min_pid = float('inf')
        for block in reversed(blocks):
            m = re.search(r'data-post="[^/]+/(\d+)"', block)
            if not m: continue
            pid = int(m.group(1))
            min_pid = min(min_pid, pid)
            
            if pid in processed_ids: continue
            
            text, story_url, photo_url = "News Update", None, None
            ts = block.find('class="tgme_widget_message_text')
            if ts != -1:
                te = block.find('>', ts)
                de = block.find('</div>', te)
                if te != -1 and de != -1:
                    raw = block[te + 1: de]
                    urls = re.findall(r'href="([^"]+)"', raw)
                    for u in urls:
                        if "t.me" not in u and "telegram.me" not in u:
                            story_url = u
                            break
                    raw = raw.replace('<br>', ' ').replace('<br/>', ' ')
                    import html
                    text = html.unescape(re.sub(r'<[^<]+?>', '', raw).strip())
            ps = block.find('tgme_widget_message_photo_wrap')
            vs = block.find('tgme_widget_message_video_thumb')
            if ps != -1:
                pm = re.search(r"background-image:url\('([^']+)'\)", block[ps:ps+1000])
                if pm: photo_url = pm.group(1)
            elif vs != -1:
                pm = re.search(r"background-image:url\('([^']+)'\)", block[vs:vs+1000])
                if pm: photo_url = pm.group(1)
                
            if text and "News Update" not in text:
                all_posts.append((pid, text, photo_url, story_url))
                if len(all_posts) >= limit: break
                
        current_url = f"https://t.me/s/{username}?before={min_pid}"
        time.sleep(1)
        
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

    while True:
        try:
            processed = get_processed_ids()
            # Fetch a deep history (up to 200 posts) so no high-grade news is missed
            new_posts = get_recent_posts(SOURCE_CHANNEL, processed, limit=200)
            
            if new_posts:
                print(f"\n📬 Fetched {len(new_posts)} unprocessed post(s)!")
                
                high_grade = []
                low_grade_all = []
                for p in new_posts:
                    if any(s in p[1] for s in HIGH_GRADE_SOURCES):
                        high_grade.append(p)
                    else:
                        low_grade_all.append(p)
                
                low_grade = low_grade_all
                # If there's a massive backlog, rescue ALL high-grade news, but drop old low-grade news
                if len(new_posts) > 15:
                    print(f"⚠️ Massive backlog detected ({len(new_posts)} posts).")
                    low_grade = low_grade_all[-5:] # Keep only the 5 newest low-grade posts
                    skipped_low = low_grade_all[:-5]
                    
                    if skipped_low:
                        add_processed_ids([p[0] for p in skipped_low])
                        print(f"  🗑️ Purged {len(skipped_low)} old low-grade posts to avoid spam blocks.")
                    print(f"  💎 Rescued {len(high_grade)} high-grade stories from the backlog for compilation!")
                        
                # 1. Process High Grade as Compilations (Groups of 3)
                for i in range(0, len(high_grade), 3):
                    group = high_grade[i:i+3]
                    success = process_compilation(group)
                    if not success:
                        print("  ❌ Compilation upload failed (likely action block). Pausing.")
                        break
                    # Mark all as processed
                    add_processed_ids([p[0] for p in group])
                    print(f"  ✅ Uploaded compilation! Marked {len(group)} posts as processed.")
                    
                    wait_time = random.randint(600, 1800)
                    print(f"  ⏳ Mandatory cooldown: Sleeping {wait_time // 60}m to prevent Sentry blocks...")
                    time.sleep(wait_time)
                
                # 2. Process Low Grade Individually
                for p in low_grade:
                    # Double check we haven't already processed it just in case
                    if p[0] in get_processed_ids(): continue
                    
                    success = process_individual(p)
                    if not success:
                        print(f"  ❌ Post #{p[0]} failed. Pausing.")
                        break
                    
                    add_processed_ids([p[0]])
                    print(f"  ✅ Uploaded post #{p[0]}.")
                    
                    wait_time = random.randint(300, 1200)
                    print(f"  ⏳ Mandatory cooldown: Sleeping {wait_time // 60}m to prevent Sentry blocks...")
                    time.sleep(wait_time)
                    
        except Exception as e:
            print(f"Polling error: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    main()
