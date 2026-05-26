import os
import requests
import time
import re
from telethon import TelegramClient, events
from PIL import Image, ImageDraw, ImageFont

def load_dotenv():
    """Loads environment variables from a local .env file if it exists."""
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
                    key = key.strip()
                    val = val.strip().strip("'").strip('"')
                    os.environ[key] = val

# Load local environment variables if available
load_dotenv()

# --- Configuration ---
# Telegram API
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
SOURCE_CHANNEL_RAW = os.getenv('TG_SOURCE_CHANNEL') # e.g., '@channelusername' or '-100123456789'

# Parse SOURCE_CHANNEL: clean up spaces/quotes and convert to integer/valid username format
SOURCE_CHANNEL = None
if SOURCE_CHANNEL_RAW:
    # Strip any accidental leading/trailing spaces or quotes (very common in GitHub Secrets)
    cleaned_channel = SOURCE_CHANNEL_RAW.strip().strip("'").strip('"')
    try:
        SOURCE_CHANNEL = int(cleaned_channel)
    except ValueError:
        # If it's a username but doesn't start with '@', and is not a URL, auto-prepend '@'
        if not cleaned_channel.startswith('@') and not cleaned_channel.startswith('http') and not '/' in cleaned_channel:
            SOURCE_CHANNEL = f"@{cleaned_channel}"
            print(f"Username cleaned: Auto-prepended '@' -> {SOURCE_CHANNEL}")
        else:
            SOURCE_CHANNEL = cleaned_channel

# Meta (FB/IG) API
FB_PAGE_ID = os.getenv('FB_PAGE_ID')
IG_USER_ID = os.getenv('IG_USER_ID')
FB_ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')

# State management (to avoid duplicates)
STATE_FILE = 'last_msg_id.txt'

def get_last_processed_id():
    """Reads the last processed message ID. Returns 0 if not found or corrupted."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    return int(content)
        except ValueError:
            print("Warning: State file was empty or corrupted. Defaulting to 0.")
    return 0

def set_last_processed_id(msg_id):
    """Writes the last processed message ID to the state file."""
    with open(STATE_FILE, 'w') as f:
        f.write(str(msg_id))

def post_to_facebook(message, image_path=None):
    """Posts text or local images natively to Facebook Page."""
    try:
        if image_path and os.path.exists(image_path):
            print(f"Uploading local photo {image_path} to Facebook...")
            url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
            payload = {
                'caption': message,
                'access_token': FB_ACCESS_TOKEN
            }
            with open(image_path, 'rb') as f:
                files = {'source': f}
                res = requests.post(url, data=payload, files=files)
        else:
            print("Posting text-only update to Facebook...")
            url = f"https://graph.facebook.com/{FB_PAGE_ID}/feed"
            payload = {
                'message': message,
                'access_token': FB_ACCESS_TOKEN
            }
            res = requests.post(url, data=payload)
        
        res_json = res.json()
        if 'error' in res_json:
            print(f"Facebook API Error: {res_json['error'].get('message')} (Code: {res_json['error'].get('code')})")
        else:
            print(f"Successfully posted to Facebook! ID: {res_json.get('id', res_json.get('post_id'))}")
        return res_json
    except Exception as e:
        print(f"Failed to post to Facebook due to exception: {e}")
        return {"error": str(e)}

def post_to_instagram(message, image_url):
    """Posts an image via a public URL to Instagram Business account (2-step process)."""
    if not image_url:
        print("Skipping Instagram: Instagram API strictly requires a public image URL.")
        return None

    # Step 1: Create Media Container
    print(f"Step 1: Creating Instagram media container for {image_url}...")
    container_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': message,
        'access_token': FB_ACCESS_TOKEN
    }
    
    try:
        res = requests.post(container_url, data=payload)
        data = res.json()
        
        if 'error' in data:
            print(f"Instagram Container Error: {data['error'].get('message')} (Code: {data['error'].get('code')})")
            return data
        
        if 'id' in data:
            creation_id = data['id']
            # Step 2: Publish Container
            print("Step 2: Publishing Instagram media container...")
            publish_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
            publish_payload = {
                'creation_id': creation_id,
                'access_token': FB_ACCESS_TOKEN
            }
            res_pub = requests.post(publish_url, data=publish_payload)
            data_pub = res_pub.json()
            
            if 'error' in data_pub:
                print(f"Instagram Publish Error: {data_pub['error'].get('message')} (Code: {data_pub['error'].get('code')})")
            else:
                print(f"Successfully posted to Instagram! Media ID: {data_pub.get('id')}")
            return data_pub
    except Exception as e:
        print(f"Failed to post to Instagram due to exception: {e}")
        return {"error": str(e)}
    return None

def get_font(font_type='bold', size=24):
    """Safely loads a clean system font, falling back to default."""
    font_paths = []
    if font_type == 'bold':
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf"
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"
        ]
        
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None

def apply_news_template(image_path, text):
    """
    Applies a professional, branded news template (BBC style) to the local image.
    Adds a dark gradient overlay at the bottom, a red branded banner, and overlays 
    the post text as a clean white headline.
    """
    try:
        print(f"Applying branded news template to {image_path}...")
        img = Image.open(image_path)
        
        # Convert to RGBA for drawing overlays
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        width, height = img.size
        
        # If the image is extremely large, resize it to a maximum of 1200px to speed up drawing
        max_dim = 1200
        if width > max_dim or height > max_dim:
            img.thumbnail((max_dim, max_dim))
            width, height = img.size
            
        # Create a drawing layer
        draw = ImageDraw.Draw(img)
        
        # 1. Add a semi-transparent dark gradient overlay at the bottom (30% height)
        overlay_height = int(height * 0.30)
        overlay = Image.new('RGBA', (width, overlay_height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(overlay_height):
            # Gradient alpha from 0 to 220
            alpha = int((y / overlay_height) * 220)
            overlay_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        
        # Paste the overlay onto the image
        img.alpha_composite(overlay, dest=(0, height - overlay_height))
        
        # Re-get draw context for the composite image
        draw = ImageDraw.Draw(img)
        
        # 2. Add a red branded tab at the bottom-left (BBC Style)
        # Red: RGB (186, 12, 47)
        red_color = (186, 12, 47, 255)
        tab_width = int(width * 0.22)
        tab_height = int(height * 0.055)
        if tab_width < 100: tab_width = 100
        if tab_height < 30: tab_height = 30
        
        tab_y_start = height - overlay_height - tab_height
        draw.rectangle([15, tab_y_start, 15 + tab_width, height - overlay_height], fill=red_color)
        
        # Draw "BREAKING" or "UPDATE" text inside the red tab
        font_size_tab = int(tab_height * 0.55)
        if font_size_tab < 12: font_size_tab = 12
        font_tab = get_font('bold', font_size_tab)
        
        text_tab = "UPDATE"
        draw.text((25, tab_y_start + int(tab_height * 0.2)), text_tab, fill=(255, 255, 255, 255), font=font_tab)
        
        # 3. Draw the headline text at the bottom
        # Clean text: remove links or extreme characters
        clean_text_lines = []
        for word in text.split():
            if not word.startswith("http") and not word.startswith("@"):
                clean_text_lines.append(word)
        clean_headline = " ".join(clean_text_lines)[:120]  # Limit to 120 chars for overlay
        if not clean_headline.strip():
            clean_headline = "News Update!"
            
        # Wrap text to fit the image width
        font_size_text = int(height * 0.045)
        if font_size_text < 16: font_size_text = 16
        if font_size_text > 36: font_size_text = 36
        font_text = get_font('bold', font_size_text)
        
        # Simple wrapping
        wrapped_text = ""
        max_chars_per_line = int(width / (font_size_text * 0.65))
        if max_chars_per_line < 15: max_chars_per_line = 15
        words = clean_headline.split()
        current_line = []
        for word in words:
            if len(" ".join(current_line + [word])) <= max_chars_per_line:
                current_line.append(word)
            else:
                wrapped_text += " ".join(current_line) + "\n"
                current_line = [word]
        wrapped_text += " ".join(current_line)
        
        # Keep only the first 2-3 lines of text
        lines = wrapped_text.split('\n')[:3]
        final_text = "\n".join(lines)
        
        # Draw text with shadow for readability
        x, y = 20, height - overlay_height + 15
        
        # Draw shadow
        draw.text((x + 2, y + 2), final_text, fill=(0, 0, 0, 255), font=font_text)
        # Draw white text
        draw.text((x, y), final_text, fill=(255, 255, 255, 255), font=font_text)
        
        # Save back as JPEG
        final_img = img.convert('RGB')
        edited_path = f"edited_{os.path.basename(image_path)}"
        final_img.save(edited_path, 'JPEG', quality=95)
        print(f"Branded news image saved successfully to {edited_path}")
        return edited_path
    except Exception as e:
        print(f"Failed to apply news template to image: {e}")
        return image_path  # Fallback to original image if editing fails

def extract_post_data(html, username, post_id):
    """Extracts text and photo URL for a specific post_id from the scraped HTML."""
    try:
        start_tag = f'data-post="{username}/{post_id}"'
        if start_tag not in html:
            return "News Update!", None
            
        idx = html.find(start_tag)
        block = html[idx:idx+15000] # Get large chunk containing the post HTML
        
        # Extract text
        text = "News Update!"
        text_start = block.find('class="tgme_widget_message_text')
        if text_start != -1:
            tag_end = block.find('>', text_start)
            div_end = block.find('</div>', tag_end)
            raw_text = block[tag_end+1:div_end]
            text = re.sub('<[^<]+?>', '', raw_text).strip()
            
        # Extract photo URL
        photo_url = None
        photo_start = block.find('class="tgme_widget_message_photo_wrap"')
        if photo_start != -1:
            style_idx = block.find('style="background-image:url(', photo_start)
            if style_idx != -1:
                url_start = style_idx + len('style="background-image:url(')
                quote = block[url_start]
                if quote in ["'", '"']:
                    url_end = block.find(quote, url_start + 1)
                    photo_url = block[url_start+1:url_end]
                else:
                    url_end = block.find(')', url_start)
                    photo_url = block[url_start:url_end]
                    
        return text, photo_url
    except Exception as e:
        print(f"Error parsing post {post_id} details: {e}")
        return "News Update!", None

async def main():
    if not all([API_ID, API_HASH, BOT_TOKEN, SOURCE_CHANNEL]):
        print("Error: Missing Telegram configuration environment variables.")
        return

    client = TelegramClient('bridge_session', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    
    # Get latest messages from channel (handle clean/empty session cache)
    try:
        entity = await client.get_entity(SOURCE_CHANNEL)
    except ValueError as e:
        print(f"\n[Error] Could not find the channel in your session cache: {e}")
        print("💡 Why this happens: Telegram bots are restricted from listing their chats (they cannot call get_dialogs).")
        print("💡 How to fix this in your .env file:")
        print("  - OPTION A (Public Channel): Set TG_SOURCE_CHANNEL to the public username (e.g., @my_channel_username).")
        print("  - OPTION B (Private Channel): Set TG_SOURCE_CHANNEL to your channel's invite link (e.g., https://t.me/+AbCdEf12345).")
        print("    (This will automatically resolve the access hash and cache the channel into your local session!)")
        print("  - OPTION C (Persistent ID): Once the session cache has populated via OPTION B at least once,")
        print("    you can safely change it back to the integer ID (like -1003892228063) and it will work forever.\n")
        await client.disconnect()
        return
    
    last_id = get_last_processed_id()
    print(f"Resuming bridge. Last processed message ID from memory: {last_id}")
    print(f"Successfully connected to channel: {entity.title} (ID: {entity.id})")
    
    # --- Startup Missed Posts Recovery (Scrapes web preview to bypass bot restrictions) ---
    clean_username = None
    if isinstance(SOURCE_CHANNEL, str) and SOURCE_CHANNEL.startswith('@'):
        clean_username = SOURCE_CHANNEL[1:]
    elif isinstance(SOURCE_CHANNEL, str) and not SOURCE_CHANNEL.startswith('http') and not '/' in SOURCE_CHANNEL:
        clean_username = SOURCE_CHANNEL
        
    if clean_username:
        print(f"Performing startup check for missed posts in public channel @{clean_username}...")
        try:
            url = f"https://t.me/s/{clean_username}"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                html = res.text
                pattern = rf'data-post="{clean_username}/(\d+)"'
                post_ids = sorted(list(set([int(x) for x in re.findall(pattern, html)])))
                missed_pids = [pid for pid in post_ids if pid > last_id]
                
                if missed_pids:
                    print(f"Found {len(missed_pids)} missed posts. Bridging them now...")
                    for pid in missed_pids:
                        text, photo_url = extract_post_data(html, clean_username, pid)
                        image_path = None
                        image_path_to_post = None
                        
                        # Download photo if exists
                        if photo_url:
                            try:
                                print(f"Downloading missed post photo from {photo_url}...")
                                img_res = requests.get(photo_url, timeout=15)
                                if img_res.status_code == 200:
                                    image_path = f"temp_missed_{pid}.jpg"
                                    with open(image_path, 'wb') as f:
                                        f.write(img_res.content)
                                    # Apply Pillow Branded News Template!
                                    image_path_to_post = apply_news_template(image_path, text)
                            except Exception as e:
                                print(f"Failed to download missed post photo: {e}")
                                image_path_to_post = image_path
                                
                        print(f"Bridging missed post {pid}...")
                        post_to_facebook(text, image_path_to_post)
                        
                        # Check for Instagram public image link
                        ig_url = None
                        if "http" in text and (".jpg" in text or ".png" in text or ".jpeg" in text):
                            for word in text.split():
                                if word.startswith("http") and any(ext in word for ext in [".jpg", ".png", ".jpeg"]):
                                    ig_url = word
                                    break
                        if ig_url:
                            post_to_instagram(text, ig_url)
                            
                        # Cleanup local files
                        if image_path and os.path.exists(image_path):
                            try: os.remove(image_path)
                            except: pass
                        if image_path_to_post and image_path_to_post != image_path and os.path.exists(image_path_to_post):
                            try: os.remove(image_path_to_post)
                            except: pass
                            
                        last_id = pid
                        set_last_processed_id(last_id)
                    print("Missed posts recovery complete!")
                else:
                    print("No missed posts found since last processed message.")
        except Exception as e:
            print(f"Missed posts recovery skipped due to error: {e}")
    # -------------------------------------------------------------------------------------

    print("Real-time News Bridge is active and listening for new messages...")

    @client.on(events.NewMessage(chats=entity))
    async def handler(event):
        nonlocal last_id
        msg = event.message
        
        # Memory Check: skip duplicates or older posts
        if msg.id <= last_id:
            return
            
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Received new channel message {msg.id}: {msg.text[:50] if msg.text else '(No Text)'}...")
        
        text = msg.text if msg.text else "News Update!"
        image_path = None
        image_path_to_post = None
        
        # Download photo locally if attached
        if msg.photo:
            try:
                print("Downloading photo attachment...")
                image_path = await client.download_media(msg.photo)
                print(f"Attachment saved to {image_path}")
                # Apply Pillow Branded News Template!
                image_path_to_post = apply_news_template(image_path, text)
            except Exception as e:
                print(f"Failed to download Telegram media: {e}")
                image_path_to_post = image_path
        
        print("Bridging message...")
        
        # 1. Post to Facebook (supports local photos uploaded natively)
        post_to_facebook(text, image_path_to_post)
        
        # 2. Post to Instagram (Only if there is a public image URL in the text, since Meta requires it)
        image_url = None
        if "http" in text and (".jpg" in text or ".png" in text or ".jpeg" in text):
            for word in text.split():
                if word.startswith("http") and any(ext in word for ext in [".jpg", ".png", ".jpeg"]):
                    image_url = word
                    break
        
        if image_url:
            post_to_instagram(text, image_url)
            
        # Update memory state
        last_id = msg.id
        set_last_processed_id(last_id)
        print(f"Saved progress to memory. Last processed message ID updated to: {last_id}")
        
        # Cleanup downloaded file to prevent local storage pollution
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"Removed temporary local photo: {image_path}")
            except Exception as e:
                print(f"Could not clean up temporary photo {image_path}: {e}")
        if image_path_to_post and image_path_to_post != image_path and os.path.exists(image_path_to_post):
            try:
                os.remove(image_path_to_post)
                print(f"Removed temporary edited photo: {image_path_to_post}")
            except Exception as e:
                print(f"Could not clean up temporary edited photo {image_path_to_post}: {e}")

    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
