# Social News Bridge 📡

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.13%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

</div>

## Overview

**Social News Bridge** is a premium automation tool that monitors a Telegram channel, transforms each news post into a stunning Instagram Reel, and publishes it with professional captions and optional background music. The bridge includes:

- **Dynamic image compositing** with blurred cinematic background, premium borders, and a red "BREAKING NEWS" banner.
- **Automatic caption generation** featuring branding (`Teds Mordare Official`), story links, hashtags, and engagement prompts.
- **Music integration** with robust retry/back‑off handling for Instagram’s rate‑limited music API.
- **Session persistence** to avoid repeated Instagram logins and intelligent challenge resolution.
- **Elegant dark‑mode gradients** and modern typography for a polished visual aesthetic.

## Features

| Feature | Description |
|---------|-------------|
| **Telegram Scraper** | Pulls recent posts from a public Telegram channel without needing an API key. |
| **Image Processing** | Resizes, blurs, and overlays the original image on a 1080×1920 canvas with premium borders. |
| **Video Generation** | Creates a 5‑second silent video (or with music) ready for Instagram Reels. |
| **Music Search & Upload** | Searches for "calming lofi" tracks, retries on 429 errors, and mixes locally when needed. |
| **Instagram Session Management** | Saves `ig_session.json` for reuse, handles login challenges via `IG_CHALLENGE_CODE`. |
| **Professional Captions** | Adds branding, removes raw URLs, includes a clickable story link, and appends lively footer & hashtags. |
| **Extensible** | Easy to swap music queries, change branding, or adapt to other platforms. |

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/social-news-bridge.git
cd social-news-bridge

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies (includes video support for instagrapi)
./venv/bin/pip install "instagrapi[video]" --no-deps
./venv/bin/pip install --no-deps "moviepy==2.2.1"
./venv/bin/pip install -r requirements.txt   # any additional deps like Pillow, requests, python-dotenv
```

> **Note:** The `instagrapi[video]` extra installs `ffmpeg`‑related Python bindings. Ensure you have the system `ffmpeg` binary installed (`sudo apt install ffmpeg`).

## Configuration

Create a `.env` file in the project root:

```dotenv
IG_USERNAME=your_instagram_username
IG_PASSWORD=your_instagram_password
TG_SOURCE_CHANNEL=@tedsxh   # Telegram channel handle (without the leading @ optional)
# Optional: Provide a verification code when Instagram triggers a challenge
IG_CHALLENGE_CODE=123456
```

- `IG_CHALLENGE_CODE` can be set once you receive the verification code via email/SMS. The script will automatically resolve the challenge.
- The bridge stores the Instagram session in `ig_session.json` after the first successful login.

## Usage

```bash
# Activate virtual env if not already active
source venv/bin/activate

# Run the bridge
python bridge.py
```

The bridge will:
1. Load the last processed Telegram post ID (`last_msg_id.txt`).
2. Poll the Telegram channel for new posts.
3. For each new post, generate an image/video, attach music (if available), and publish a Reel.
4. Update the state file so it resumes gracefully on restart.

## Customisation

- **Music Query**: Change the search term in `post_to_instagram` (`client.search_music("calming lofi")`).
- **Branding**: Edit `clean_and_format_caption` to modify the intro, footer, or hashtags.
- **Visual Style**: Adjust colors, gradients, or border thickness in `apply_news_template`.

## Troubleshooting

- **Login Challenges**: If Instagram asks for a verification code, set `IG_CHALLENGE_CODE` in `.env` or provide it when prompted.
- **Rate‑Limit (429) on Music**: The bridge already retries three times with exponential back‑off. If failures persist, consider increasing `max_search_retries` in `post_to_instagram`.
- **FFmpeg Errors**: Ensure the system `ffmpeg` binary is in your `$PATH`.

## License

MIT License – see the `LICENSE` file for details.

---

*Built with ❤️ by the Teds Mordare Official team.*