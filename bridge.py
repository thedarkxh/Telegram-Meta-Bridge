import os
import requests
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

# --- Configuration ---
# Telegram API
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
SOURCE_CHANNEL_RAW = os.getenv('TG_SOURCE_CHANNEL') # e.g., '@channelusername' or '-100123456789'

# Parse SOURCE_CHANNEL: convert to integer if it represents one (Telethon needs int for channel IDs)
SOURCE_CHANNEL = None
if SOURCE_CHANNEL_RAW:
    try:
        SOURCE_CHANNEL = int(SOURCE_CHANNEL_RAW)
    except ValueError:
        SOURCE_CHANNEL = SOURCE_CHANNEL_RAW

# Meta (FB/IG) API
FB_PAGE_ID = os.getenv('FB_PAGE_ID')
IG_USER_ID = os.getenv('IG_USER_ID')
FB_ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')

# State management (to avoid duplicates)
STATE_FILE = 'last_msg_id.txt'

def get_last_processed_id():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    return int(content)
        except ValueError:
            pass
    return 0

def set_last_processed_id(msg_id):
    with open(STATE_FILE, 'w') as f:
        f.write(str(msg_id))

def post_to_facebook(message, image_url=None):
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos" if image_url else f"https://graph.facebook.com/{FB_PAGE_ID}/feed"
    payload = {
        'message': message,
        'access_token': FB_ACCESS_TOKEN
    }
    if image_url:
        payload['url'] = image_url
    
    res = requests.post(url, data=payload)
    return res.json()

def post_to_instagram(message, image_url):
    # IG requires a two-step process: 1. Create Container, 2. Publish Container
    # 1. Create Media Container
    container_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': message,
        'access_token': FB_ACCESS_TOKEN
    }
    res = requests.post(container_url, data=payload)
    data = res.json()
    
    if 'id' in data:
        creation_id = data['id']
        # 2. Publish Container
        publish_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': FB_ACCESS_TOKEN
        }
        res_pub = requests.post(publish_url, data=publish_payload)
        return res_pub.json()
    return data

async def main():
    client = TelegramClient('bridge_session', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    
    last_id = get_last_processed_id()
    
    # Get latest messages from channel
    try:
        entity = await client.get_entity(SOURCE_CHANNEL)
    except ValueError as e:
        print(f"Entity not found in clean session cache ({e}). Fetching dialogs to populate cache...")
        # Since GitHub Actions runs on a fresh VM every time, the session database is empty.
        # Fetching dialogs populates the cache with all channels/chats the bot is a member of.
        await client.get_dialogs()
        entity = await client.get_entity(SOURCE_CHANNEL)
        
    messages = await client.get_messages(entity, limit=10)
    
    new_messages = []
    for msg in messages:
        if msg.id > last_id:
            new_messages.append(msg)
        else:
            break
            
    # Process messages in chronological order (oldest first)
    for msg in reversed(new_messages):
        text = msg.text if msg.text else "News Update!"
        image_path = None
        
        if msg.photo:
            # Telegram doesn't provide a public URL for photos by default
            # In a real bridge, you'd need to upload the photo to a public host (like S3 or Imgur)
            # since Meta API requires a public URL.
            # For this implementation, we assume the bot is handling a URL or we'd need an upload step.
            print(f"Skipping photo for msg {msg.id}: Meta requires public URLs.")
            # If the message contains a link to an image, you can extract it.
        
        # If the message has a link, we can try to use that as the image source if it's a direct image link
        # or just post the text.
        
        print(f"Bridging message {msg.id}...")
        post_to_facebook(text)
        if image_path:
            post_to_instagram(text, image_path)
            
        last_id = msg.id

    set_last_processed_id(last_id)
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
