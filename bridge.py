import os
import requests
from telethon import TelegramClient

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

async def main():
    if not all([API_ID, API_HASH, BOT_TOKEN, SOURCE_CHANNEL]):
        print("Error: Missing Telegram configuration environment variables.")
        return

    client = TelegramClient('bridge_session', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    
    last_id = get_last_processed_id()
    print(f"Resuming bridge. Last processed message ID: {last_id}")
    
    # Get latest messages from channel (handle empty session cache on fresh runners)
    try:
        entity = await client.get_entity(SOURCE_CHANNEL)
    except ValueError as e:
        print(f"Channel not found in empty session cache ({e}). Fetching active dialogs to populate...")
        await client.get_dialogs()
        entity = await client.get_entity(SOURCE_CHANNEL)
    
    print(f"Successfully connected to channel: {entity.title} (ID: {entity.id})")
    messages = await client.get_messages(entity, limit=10)
    
    new_messages = []
    for msg in messages:
        if msg.id > last_id:
            new_messages.append(msg)
        else:
            break
            
    if not new_messages:
        print("No new messages found.")
        await client.disconnect()
        return

    print(f"Found {len(new_messages)} new message(s) to process.")
    
    # Process messages in chronological order (oldest first)
    for msg in reversed(new_messages):
        text = msg.text if msg.text else "News Update!"
        image_path = None
        
        # Download photo locally if attached
        if msg.photo:
            try:
                print(f"Downloading Telegram attachment for message {msg.id}...")
                image_path = await client.download_media(msg.photo)
                print(f"Attachment saved to {image_path}")
            except Exception as e:
                print(f"Failed to download Telegram media for message {msg.id}: {e}")
        
        print(f"Bridging message {msg.id}...")
        
        # 1. Post to Facebook (supports local photos uploaded natively)
        post_to_facebook(text, image_path)
        
        # 2. Post to Instagram (Only if there is a public image URL in the text, since Meta requires it)
        # Note: Local files cannot be sent to Instagram directly.
        # We check if there's an image link in the post text, otherwise we skip Instagram.
        image_url = None
        if "http" in text and (".jpg" in text or ".png" in text or ".jpeg" in text):
            # Extract basic URL containing image signature
            for word in text.split():
                if word.startswith("http") and any(ext in word for ext in [".jpg", ".png", ".jpeg"]):
                    image_url = word
                    break
        
        if image_url:
            post_to_instagram(text, image_url)
            
        last_id = msg.id
        
        # Cleanup downloaded file to prevent local storage pollution
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"Removed temporary local photo: {image_path}")
            except Exception as e:
                print(f"Could not clean up temporary photo {image_path}: {e}")

    set_last_processed_id(last_id)
    print(f"Successfully processed messages up to ID {last_id}.")
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
