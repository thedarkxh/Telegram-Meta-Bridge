# 📡 Telegram-to-Instagram Reels News Bridge

A production-grade, highly optimized Python bridge that automatically polls a Telegram channel, extracts breaking news posts, formats the uncropped images into premium vertical Instagram Reels (`1080x1920`), attaches calming lo-fi audio tracks, parses professional captions, and publishes them natively to Instagram.

---

## 🚀 Features

*   **📺 Premium Border-Touching Reels Layout:** 
    *   **No-Crop Visuals:** Completely preserves the original photo without cropping or squishing.
    *   **Cinematic Presentation:** Landscape and square images are scaled to touch the screen borders horizontally (exact `1080px` canvas width) and separated by elegant horizontal boundary lines over a heavily blurred backdrop (`GaussianBlur(45)`) with a dark mask overlay. Tall portrait images are fitted inside a safe vertical viewport.
*   **🎵 Automated Calming Audio Sync:**
    *   Query-based programmatic integration with Instagram's live audio trends. Auto-selects and attaches soothing, high-engagement calming lo-fi tracks (like *Calming Lofi* by *Lofi Fruits Music*) using the stable `clip_upload_with_music` API to maximize Reels algorithm discoverability.
    *   *Mute Fallback:* Automatically falls back to a high-quality locally compiled silent audio track (`anullsrc`) if Instagram's music databases are temporarily unreachable, ensuring 100% publishing uptime.
*   **✍️ Clean Typography & ToFus Resolution:**
    *   **No Rectangle Boxes:** Automatically filters out graphic emojis and variation selectors from the image title overlays. This completely resolves the Linux font rendering limitation that caused empty "rectangle box" (tofu) characters to appear on the image.
    *   **Source Extraction:** Parses `"Source: BBC News"` or similar labels, removes them from the main headline to save space, and renders them at the bottom-left of the canvas in a smaller, elegant font.
    *   **Headline Cleanup:** Automatically filters out promotional, navigation, and link-related phrases from the image headline block.
*   **📝 Professional Caption Cleansing:**
    *   Strips ugly, non-clickable raw URLs and promotional telegram join banners from captions. Normalizes spacing into neat paragraphs, and appends a curated set of high-engagement news hashtags (`#news #breakingnews #globalnews #worldnews #newsupdate #currentaffairs`).
*   **🛠️ Self-Healing Process Manager (`run_local.py`):**
    *   A robust runner script wraps the bridge. If the process exits due to temporary network loss, session timeouts, or API blocks, it automatically logs a warning, waits 10 seconds, and performs a clean restart.

---

## 📂 Project Structure

*   `bridge.py` — The core logic containing the HTML parsing loop, Pillow image composition engine, professional caption cleanup, and stable `instagrapi` Reels publisher.
*   `run_local.py` — Self-healing manager loop that runs the bridge persistently in the background.
*   `last_msg_id.txt` — Memory state file tracking the last successfully processed message ID to prevent duplicate posts.
*   `.env` — Local configuration file containing sensitive credentials.

---

## ⚙️ Environment Variables (`.env`)

Create a `.env` file in the root directory:

```env
# Telegram Configuration
TG_SOURCE_CHANNEL=@tedsxh

# Instagram Configuration
IG_USERNAME=your_instagram_username
IG_PASSWORD=your_instagram_password
```

---

## 🚀 Quick Start

### 1. Install System Dependencies
Ensure `ffmpeg` and system TrueType fonts are installed:
```bash
sudo apt update
sudo apt install -y ffmpeg fonts-dejavu-core
```

### 2. Set Up Virtual Environment & Packages
Initialize the Python virtual environment and install the required modules:
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 3. Launch the Persistent Sync Bridge
Start the self-healing process manager loop:
```bash
python3 run_local.py
```
This manager will monitor the feed, resume parsing from the last processed message, and automatically mirror posts in real-time.