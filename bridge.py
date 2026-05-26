import os
import requests
import time
import re
import wave
import math
import struct
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def load_dotenv():
    dotenv_path = '.env'
    if os.path.exists(dotenv_path):
        print("Loading configuration from local .env file...")
        with open(dotenv_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip("'").strip('"')

load_dotenv()

IG_USERNAME = os.getenv('IG_USERNAME')
IG_PASSWORD = os.getenv('IG_PASSWORD')
SOURCE_CHANNEL_RAW = os.getenv('TG_SOURCE_CHANNEL')

SOURCE_CHANNEL = None
if SOURCE_CHANNEL_RAW:
    cleaned = SOURCE_CHANNEL_RAW.strip().strip("'").strip('"')
    if not cleaned.startswith('@') and not cleaned.startswith('http') and '/' not in cleaned:
        SOURCE_CHANNEL = cleaned
    else:
        SOURCE_CHANNEL = cleaned.lstrip('@').split('/')[-1]

STATE_FILE = 'last_msg_id.txt'

from instagrapi import Client
ig_client = None

def get_ig_client():
    global ig_client
    if ig_client is not None:
        return ig_client
    
    print(f"Logging into Instagram as {IG_USERNAME}...")
    ig_client = Client()
    try:
        ig_client.login(IG_USERNAME, IG_PASSWORD)
        print("✅ Instagram login successful!")
        return ig_client
    except Exception as e:
        print(f"❌ Instagram login failed: {e}")
        ig_client = None
        return None

def get_last_processed_id():
    if os.path.exists(STATE_FILE):
        try: return int(open(STATE_FILE).read().strip())
        except ValueError: pass
    return 0

def set_last_processed_id(msg_id):
    with open(STATE_FILE, 'w') as f: f.write(str(msg_id))

def create_news_video(image_path, output_path="news_post.mp4"):
    try:
        print(f"Compiling silent video for Instagram Reels...")
        if os.path.exists(output_path): os.remove(output_path)
        cmd = [
            'ffmpeg', '-y', '-loop', '1', '-i', image_path,
            '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-c:v', 'libx264', '-tune', 'stillimage',
            '-c:a', 'aac', '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
            '-shortest', '-t', '5', output_path
        ]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        return output_path if r.returncode == 0 else None
    except Exception: return None

def post_to_instagram(message, video_path, img_path):
    print(f"📤 Uploading video to Instagram...")
    try:
        client = get_ig_client()
        if not client: return None
        
        media = None
        try:
            print("🎵 Searching for calming lofi music...")
            tracks = client.search_music("calming lofi")
            if tracks:
                track = tracks[0]
                print(f"🔥 Selected calming track: '{track.title}' by {track.display_artist} (ID: {track.id})")
                
                # If uri is None, populate it from progressive_download_url to support local mixing
                if not track.uri and track.progressive_download_url:
                    track.uri = track.progressive_download_url
                
                print("📤 Uploading Reel with calming music track (audio mixed locally)...")
                media = client.clip_upload_as_reel_with_music(
                    path=video_path,
                    caption=message,
                    track=track
                )
                print(f"✅ Posted to Instagram with calming music! ID: {media.id}")
            else:
                print("ℹ️ No calming music tracks found. Falling back to standard upload...")
        except Exception as music_err:
            print(f"⚠️ Could not attach calming music ({music_err}). Falling back to silent upload...")
            
        # Fallback to standard Reel upload if music upload was not successful
        if not media:
            print("📤 Uploading standard silent Reel...")
            media = client.clip_upload(video_path, message, thumbnail=img_path)
            print(f"✅ Posted standard Reel to Instagram! ID: {media.id}")
            
        return media
    except Exception as e:
        print(f"❌ Instagram upload error: {e}")
        return None

def get_font(size=24):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def create_default_bg(output_path="default_bg.jpg"):
    w, h = 1080, 1920
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    # Professional dark blue gradient
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
        
        # 1. Create blurred background canvas covering 1080x1920
        if img_ratio > target_ratio:
            bg_h = target_h
            bg_w = int(bg_h * img_ratio)
        else:
            bg_w = target_w
            bg_h = int(bg_w / img_ratio)
            
        bg_img = original_img.resize((bg_w, bg_h), Image.LANCZOS)
        
        # Center crop bg_img to exactly 1080x1920
        bg_left = (bg_w - target_w) / 2
        bg_top = (bg_h - target_h) / 2
        bg_right = (bg_w + target_w) / 2
        bg_bottom = (bg_h + target_h) / 2
        bg_img = bg_img.crop((bg_left, bg_top, bg_right, bg_bottom))
        
        # Apply heavy blur for cinematic visual effect
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(45))
        
        canvas = bg_img.copy()
        draw = ImageDraw.Draw(canvas)
        
        # Apply premium semi-transparent dark mask overlay over the blurred canvas
        overlay = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 130))
        canvas.alpha_composite(overlay)
        
        # 2. Fit the uncropped original sharp image on top (Touch borders horizontally if landscape/square)
        if img_ratio >= target_ratio:
            # Image is landscape or square. Touch horizontal borders!
            sharp_w = target_w
            sharp_h = int(sharp_w / img_ratio)
            paste_x = 0
            paste_y = int(120 + (1100 - sharp_h) / 2)
        else:
            # Image is portrait/vertical. Fit it vertically within safe region.
            sharp_h = 1100
            sharp_w = int(sharp_h * img_ratio)
            paste_x = int((target_w - sharp_w) / 2)
            paste_y = 120
            
        sharp_img = original_img.resize((sharp_w, sharp_h), Image.LANCZOS)
        
        # Draw sleek borders for full-width band or a box border for vertical images
        border_layer = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border_layer)
        if paste_x == 0:
            # Draw professional top/bottom border separator lines
            border_draw.line([(0, paste_y - 2), (target_w, paste_y - 2)], fill=(255, 255, 255, 140), width=2)
            border_draw.line([(0, paste_y + sharp_h + 1), (target_w, paste_y + sharp_h + 1)], fill=(255, 255, 255, 140), width=2)
        else:
            # Draw outline border around centered tall image
            border_draw.rectangle(
                [paste_x - 2, paste_y - 2, paste_x + sharp_w + 2, paste_y + sharp_h + 2],
                outline=(255, 255, 255, 180),
                width=2
            )
        canvas.alpha_composite(border_layer)
        canvas.alpha_composite(sharp_img, dest=(paste_x, paste_y))
        
        # 3. Extract source metadata from text
        source_match = re.search(r'(?i)(source:\s*[^\n]+)', text)
        source_text = ""
        if source_match:
            source_text = source_match.group(1).strip()
            # Clean emojis and variation selectors from source label
            source_text = re.sub(r'[\U00010000-\U0010ffff]', '', source_text)
            source_text = re.sub(r'[\u2600-\u27BF]', '', source_text)
            source_text = re.sub(r'[\ufe00-\ufe0f\u200d]', '', source_text)
            source_text = " ".join(source_text.split()).strip()
            
        # 4. Clean and format headline base (Removing source/links/emojis/tofu boxes)
        headline_base = text
        if source_match:
            headline_base = headline_base.replace(source_match.group(1), "")
            
        headline_base = re.sub(r'(?i)read\s+full(\s+story)?', '', headline_base)
        headline_base = re.sub(r'(?i)related:\s*join\s+teds\s+mordare\s+official.*', '', headline_base)
        headline_base = re.sub(r'(?i)join\s+teds\s+mordare.*', '', headline_base)
        
        # Strip raw URLs and mentions
        headline_base = " ".join(w for w in headline_base.split() if not w.startswith("http") and not w.startswith("@"))
        
        # Strip all emojis and variation selectors
        clean_headline = re.sub(r'[\U00010000-\U0010ffff]', '', headline_base)
        clean_headline = re.sub(r'[\u2600-\u27BF]', '', clean_headline)
        clean_headline = re.sub(r'[\ufe00-\ufe0f\u200d]', '', clean_headline)
        clean_headline = " ".join(clean_headline.split()).strip()
        
        # Strip "BREAKING NEWS" from the clean headline to avoid duplication with the red banner
        clean_headline = re.sub(r'(?i)^\s*breaking\s+news\s*', '', clean_headline).strip()
        clean_headline = clean_headline[:180] or "News Update"
        
        # 5. Render Red Banner & Title Block
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
        
        # 6. Render Source Text in bottom-left in a smaller professional font
        if source_text:
            font_source = get_font(24)
            draw.text((40, 1820), source_text, fill=(200, 200, 200, 220), font=font_source)
            
        out = f"edited_{os.path.basename(image_path)}"
        canvas.convert('RGB').save(out, 'JPEG', quality=95)
        return out
    except Exception as e:
        print(f"Error applying template: {e}")
        return image_path

def get_recent_posts(username, last_id, hours_back=24):
    from datetime import datetime, timezone, timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    
    all_posts = {}
    current_url = f"https://telegram.me/s/{username}"
    pages_fetched = 0
    
    while pages_fetched < 50: # Safety limit
        pages_fetched += 1
        try:
            r = requests.get(current_url, timeout=10)
            if r.status_code != 200: break
            html = r.text
        except: break
            
        blocks = html.split('<div class="tgme_widget_message text_not_supported_wrap js-widget_message"')[1:]
        if not blocks: blocks = html.split('tgme_widget_message ')[1:]
        if not blocks: break
        
        oldest_dt = datetime.now(timezone.utc)
        min_pid = float('inf')
        
        for block in blocks:
            m = re.search(r'data-post="[^/]+/(\d+)"', block)
            if not m: continue
            pid = int(m.group(1))
            min_pid = min(min_pid, pid)
            if pid <= last_id: continue
            
            # Extract time
            post_time = datetime.now(timezone.utc)
            tm = re.search(r'<time[^>]+datetime="([^"]+)"', block)
            if tm:
                try: post_time = datetime.fromisoformat(tm.group(1).replace('Z', '+00:00'))
                except: pass
            
            oldest_dt = min(oldest_dt, post_time)
            if post_time < cutoff: continue
                
            # Extract text and story link
            text = "News Update"
            story_url = None
            ts = block.find('class="tgme_widget_message_text')
            if ts != -1:
                te = block.find('>', ts)
                de = block.find('</div>', te)
                if te != -1 and de != -1:
                    raw = block[te + 1: de]
                    # Extract the first link that is not a telegram join channel link
                    url_match = re.search(r'href="([^"]+)"', raw)
                    if url_match:
                        url_val = url_match.group(1)
                        if "t.me" not in url_val and "telegram.me" not in url_val:
                            story_url = url_val
                    raw = raw.replace('<br>', ' ').replace('<br/>', ' ')
                    text = re.sub(r'<[^<]+?>', '', raw).strip()
                    
            # Extract photo
            photo_url = None
            ps = block.find('tgme_widget_message_photo_wrap')
            if ps != -1:
                pm = re.search(r"background-image:url\('([^']+)'\)", block[ps:ps+1000])
                if pm: photo_url = pm.group(1)
                
            all_posts[pid] = (pid, text, photo_url, story_url)
            
        if oldest_dt < cutoff or min_pid <= last_id or min_pid == float('inf'):
            break
            
        current_url = f"https://telegram.me/s/{username}?before={min_pid}"
        time.sleep(1)
        
    return sorted(list(all_posts.values()), key=lambda x: x[0])

def clean_and_format_caption(text, story_url=None):
    if not text:
        return "Teds Mordare Official News Update | @tedsxh\n\n#news #breakingnews #globalnews #worldnews #tedsmordare"
        
    lines = text.split('\n')
    cleaned_lines = []
    
    # Custom intro credit branding block at the top
    intro = "📡 Teds Mordare Official News Update | @tedsxh 📡\n"
    cleaned_lines.append(intro)
    
    for line in lines:
        line = line.strip()
        if not line:
            cleaned_lines.append("")
            continue
            
        # Remove lines that only contain raw URLs or promotional prompts
        if "READ FULL STORY" in line or "read full story" in line.lower():
            continue
        if "join teds mordare" in line.lower() or "t.me/" in line.lower():
            continue
            
        # Clean up any residual raw HTTP URLs from the caption text to avoid messy text
        words = line.split()
        cleaned_words = [w for w in words if not w.startswith("http://") and not w.startswith("https://")]
        cleaned_line = " ".join(cleaned_words)
        
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
            
    # Reconstruct the caption with elegant spacing
    raw_caption = "\n".join(cleaned_lines)
    # Remove consecutive empty lines (max 1 empty line)
    raw_caption = re.sub(r'\n{3,}', '\n\n', raw_caption).strip()
    
    # Add clickable story link information if present
    link_section = ""
    if story_url:
        link_section = f"\n\n🔗 FULL STORY LINK (Copy & paste or check bio):\n👉 {story_url}"
    else:
        link_section = "\n\n🔗 Full story link available in bio!"
        
    # Custom lively branding/engagement footer
    footer = (
        "\n\n💬 What are your thoughts on this update? Let us know in the comments below! 👇"
        "\n\n🔔 Stay connected with the truth! Follow Teds Mordare Official on Telegram: @tedsxh"
    )
    
    # Append premium professional hashtags
    hashtags = "\n\n#news #breakingnews #globalnews #worldnews #newsupdate #currentaffairs #trending #tedsmordare"
    return raw_caption + link_section + footer + hashtags

def process_and_post(image_path, text, msg_id, story_url=None):
    try:
        edited = apply_news_template(image_path, text)
        video = create_news_video(edited, f"news_video_{msg_id}.mp4")
        success = False
        if video:
            formatted_caption = clean_and_format_caption(text, story_url)
            res = post_to_instagram(formatted_caption, video, edited)
            success = res is not None
        return success
    finally:
        for fp in [f"edited_{os.path.basename(image_path)}", f"news_video_{msg_id}.mp4", image_path]:
            if fp and os.path.exists(fp) and "default_bg" not in fp:
                try: os.remove(fp)
                except: pass

def main():
    if not IG_USERNAME or not IG_PASSWORD or not SOURCE_CHANNEL:
        print("❌ Missing config in .env. Check IG_USERNAME, IG_PASSWORD, TG_SOURCE_CHANNEL.")
        return
        
    last_id = get_last_processed_id()
    print(f"\n{'='*55}\n  📡 Bridge active — monitoring: @{SOURCE_CHANNEL}\n  💾 Resuming from ID: {last_id}\n{'='*55}\n")
    
    while True:
        try:
            new_posts = get_recent_posts(SOURCE_CHANNEL, last_id)
            if new_posts:
                print(f"\n📬 Found {len(new_posts)} new post(s)!")
                for pid, text, photo_url, story_url in new_posts:
                    print(f"  ⏭ Processing post #{pid}...")
                    img_path = "default_bg.jpg"
                    
                    if photo_url:
                        try:
                            r = requests.get(photo_url, timeout=15)
                            if r.status_code == 200:
                                img_path = f"temp_{pid}.jpg"
                                with open(img_path, 'wb') as f: f.write(r.content)
                        except: pass
                    else:
                        print(f"  ℹ️ No photo in post #{pid}. Generating default News background.")
                        create_default_bg(img_path)
                        
                    success = process_and_post(img_path, text, pid, story_url)
                    if not success:
                        print(f"  ❌ Post #{pid} failed (likely token expiration). Will retry next cycle.")
                        break # Stop processing to avoid skipping posts
                        
                    last_id = pid
                    set_last_processed_id(last_id)
                    print(f"  ✅ Finished post #{pid} (Memory updated: {last_id})")
        except Exception as e:
            print(f"Polling error: {e}")
            
        time.sleep(30)

if __name__ == "__main__":
    main()
