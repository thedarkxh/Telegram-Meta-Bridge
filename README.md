# Telegram to Meta News Bridge

A production-ready Python bridge that monitors a Telegram channel and automatically mirrors posts (text and native photos) to a Facebook Page and Instagram Business account using GitHub Actions.

## 🚀 Features

- **Automated Mirroring**: Runs every 30 minutes via GitHub Actions cron, with instant manual trigger and trigger-on-push options.
- **Natively Mirror Telegram Photos**: Automatically downloads photo attachments from Telegram and uploads them to Facebook using `multipart/form-data`.
- **Instagram Auto-Detection**: Detects public image links inside Telegram posts and automatically publishes them to your connected Instagram Business timeline.
- **Smart Duplicate Prevention**: Tracks the latest successfully bridged message ID in `last_msg_id.txt` to guarantee zero duplicated posts.
- **State-of-the-Art Reliability**: Includes empty session recovery (`get_dialogs`) for seamless operation inside clean, ephemeral CI/CD environments.

---

## 🛠️ Repository Secrets Required

Configure the following secrets in your repository settings under **Settings ➔ Secrets and variables ➔ Actions**:

| Secret Name | Description |
|---|---|
| `TG_API_ID` | Telegram Developer API ID from `my.telegram.org` |
| `TG_API_HASH` | Telegram Developer API Hash from `my.telegram.org` |
| `TG_BOT_TOKEN` | Telegram Bot token from `@BotFather` |
| `TG_SOURCE_CHANNEL` | Numeric Telegram Channel ID or Username |
| `FB_PAGE_ID` | Your Facebook Page ID |
| `IG_USER_ID` | Your Instagram Business Account ID |
| `FB_ACCESS_TOKEN` | A never-expiring Facebook Page Access Token |

---

## 📂 Project Structure

- `bridge.py` - Core logic containing the Telethon client, local file downloads, and Meta Graph API publishers.
- `last_msg_id.txt` - Tracking state file storing the last processed message ID.
- `.github/workflows/bridge1.yml` - Automation workflow running on a schedule, dispatch, and code push.