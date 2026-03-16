#!/usr/bin/env python3
"""
Telegram Media Collector for The Lua Tsuki Show.
Polls the Telegram group for new photos, videos, and documents,
downloads them, and saves them to the appropriate content folders.

Since OpenClaw also uses getUpdates on the same bot token,
this script temporarily pauses the gateway during collection.

Usage:
  python3 media_collector.py           # Run once (poll latest)
  python3 media_collector.py --watch   # Run continuously (poll every 60s)
"""

import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

# Config
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-5106063868")

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PHOTOS_DIR = os.path.join(BASE_DIR, "content", "fotos", "telegram")
VIDEOS_DIR = os.path.join(BASE_DIR, "content", "videos", "telegram")
DOCS_DIR = os.path.join(BASE_DIR, "content", "docs", "telegram")
STATE_FILE = os.path.join(BASE_DIR, ".telegram_offset")


def ensure_dirs():
    for d in [PHOTOS_DIR, VIDEOS_DIR, DOCS_DIR]:
        os.makedirs(d, exist_ok=True)


def load_offset():
    try:
        with open(STATE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_offset(offset):
    with open(STATE_FILE, "w") as f:
        f.write(str(offset))


def telegram_api(method, params=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_file(file_id, save_path):
    """Download a file from Telegram by file_id."""
    result = telegram_api("getFile", {"file_id": file_id})
    if not result.get("ok"):
        return False
    file_path = result["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    urllib.request.urlretrieve(download_url, save_path)
    return True


def process_update(update):
    """Process a single Telegram update, downloading any media."""
    msg = update.get("message") or update.get("channel_post")
    if not msg:
        return

    # Only process messages from our group
    chat_id = str(msg.get("chat", {}).get("id", ""))
    if chat_id != str(CHAT_ID):
        return

    msg_id = msg.get("message_id", 0)
    sender = msg.get("from", {}).get("first_name", "unknown")
    date = datetime.fromtimestamp(msg.get("date", 0))
    date_str = date.strftime("%Y%m%d_%H%M%S")
    caption = msg.get("caption", "")

    downloaded = []

    # Photos (Telegram sends multiple sizes, grab the largest)
    if "photo" in msg:
        photo = msg["photo"][-1]  # Largest size
        file_id = photo["file_id"]
        filename = f"{date_str}_msg{msg_id}_{sender}.jpg"
        save_path = os.path.join(PHOTOS_DIR, filename)
        if not os.path.exists(save_path):
            if download_file(file_id, save_path):
                downloaded.append(("photo", save_path))
                # Save caption as sidecar
                if caption:
                    with open(save_path + ".txt", "w", encoding="utf-8") as f:
                        f.write(f"From: {sender}\nCaption: {caption}\n")

    # Videos
    if "video" in msg:
        video = msg["video"]
        file_id = video["file_id"]
        ext = video.get("mime_type", "video/mp4").split("/")[-1]
        filename = f"{date_str}_msg{msg_id}_{sender}.{ext}"
        save_path = os.path.join(VIDEOS_DIR, filename)
        if not os.path.exists(save_path):
            if download_file(file_id, save_path):
                downloaded.append(("video", save_path))
                if caption:
                    with open(save_path + ".txt", "w", encoding="utf-8") as f:
                        f.write(f"From: {sender}\nCaption: {caption}\n")

    # Video notes (circle videos)
    if "video_note" in msg:
        vn = msg["video_note"]
        file_id = vn["file_id"]
        filename = f"{date_str}_msg{msg_id}_{sender}_videonote.mp4"
        save_path = os.path.join(VIDEOS_DIR, filename)
        if not os.path.exists(save_path):
            if download_file(file_id, save_path):
                downloaded.append(("video_note", save_path))

    # Animations (GIFs)
    if "animation" in msg:
        anim = msg["animation"]
        file_id = anim["file_id"]
        filename = f"{date_str}_msg{msg_id}_{sender}.gif.mp4"
        save_path = os.path.join(PHOTOS_DIR, filename)
        if not os.path.exists(save_path):
            if download_file(file_id, save_path):
                downloaded.append(("gif", save_path))

    # Documents (PDFs, etc.)
    if "document" in msg:
        doc = msg["document"]
        file_id = doc["file_id"]
        orig_name = doc.get("file_name", "document")
        filename = f"{date_str}_msg{msg_id}_{orig_name}"
        save_path = os.path.join(DOCS_DIR, filename)
        if not os.path.exists(save_path):
            if download_file(file_id, save_path):
                downloaded.append(("document", save_path))

    for media_type, path in downloaded:
        print(f"  [{media_type}] {os.path.basename(path)}")

    return len(downloaded)


def find_openclaw_pid():
    """Find the PID of openclaw-gateway if running."""
    try:
        out = subprocess.check_output(
            ["pgrep", "-f", "openclaw-gateway"], text=True
        ).strip()
        pids = [int(p) for p in out.split("\n") if p.strip()]
        return pids[0] if pids else None
    except (subprocess.CalledProcessError, ValueError):
        return None


def pause_gateway():
    """Pause OpenClaw gateway with SIGSTOP so it releases the polling lock."""
    pid = find_openclaw_pid()
    if pid:
        os.kill(pid, signal.SIGSTOP)
        time.sleep(1)  # Let Telegram release the lock
        return pid
    return None


def resume_gateway(pid):
    """Resume OpenClaw gateway with SIGCONT."""
    if pid:
        try:
            os.kill(pid, signal.SIGCONT)
        except ProcessLookupError:
            pass


def poll_once():
    """Poll for new updates and download media.
    Temporarily pauses OpenClaw gateway to avoid 409 conflict."""
    gateway_pid = pause_gateway()
    try:
        return _do_poll()
    finally:
        resume_gateway(gateway_pid)


def _do_poll():
    """Internal poll logic."""
    offset = load_offset()
    params = {"timeout": "5", "allowed_updates": "message,channel_post"}
    if offset > 0:
        params["offset"] = str(offset)

    try:
        result = telegram_api("getUpdates", params)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"Poll error: {e}")
        return 0

    if not result.get("ok"):
        return 0

    updates = result.get("result", [])
    total_downloaded = 0

    for update in updates:
        update_id = update["update_id"]
        count = process_update(update)
        if count:
            total_downloaded += count
        # Always advance offset past this update
        if update_id >= offset:
            offset = update_id + 1

    if updates:
        save_offset(offset)

    return total_downloaded


def main():
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)

    ensure_dirs()
    watch = "--watch" in sys.argv

    if watch:
        print(f"Watching Telegram group {CHAT_ID} for media...")
        print(f"Photos -> {PHOTOS_DIR}")
        print(f"Videos -> {VIDEOS_DIR}")
        print(f"Docs   -> {DOCS_DIR}")
        print("Press Ctrl+C to stop.\n")
        while True:
            count = poll_once()
            if count > 0:
                print(f"  Downloaded {count} file(s)")
            time.sleep(60)
    else:
        print("Polling for new media...")
        count = poll_once()
        print(f"Downloaded {count} file(s)")


if __name__ == "__main__":
    main()
