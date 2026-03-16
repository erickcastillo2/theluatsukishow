#!/usr/bin/env python3
"""
Main Production Runner for The Lua Tsuki Show.
Orchestrates the full content pipeline:
  1. Generate script (AI)
  2. Generate narration (TTS)
  3. Assemble video (FFmpeg)
  4. Generate thumbnail (Pillow)
  5. Notify via Telegram

Usage:
  python3 produce.py                    # Random theme
  python3 produce.py "Lua va al vet"    # Custom theme
"""

import asyncio
import json
import os
import sys
import urllib.request
import urllib.error

# Add src dir to path
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)

from generate_script import generate_script
from generate_narration import generate_narration
from generate_thumbnail import generate_thumbnail
from assemble_video import assemble_video

# Telegram config
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-5106063868")


def notify_telegram(message, video_path=None, thumb_path=None):
    """Send notification to Telegram group."""
    if not TELEGRAM_BOT_TOKEN:
        print("(Telegram notification skipped — no TELEGRAM_BOT_TOKEN set)")
        return

    # Send text message
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }).encode("utf-8")

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        urllib.request.urlopen(req, timeout=15)
        print("Telegram notification sent!")
    except urllib.error.URLError as e:
        print(f"Telegram notification failed: {e}")


async def produce(theme=None):
    """Run the full production pipeline."""
    print("=" * 60)
    print("  THE LUA TSUKI SHOW — Content Production Pipeline")
    print("=" * 60)

    # Step 1: Generate Script
    print("\n[1/5] Generating script...")
    script_path, script = generate_script(theme)

    # Step 2: Generate Narration
    print("\n[2/5] Generating narration...")
    audio_path, srt_path = await generate_narration(script_path)

    # Step 3: Generate Thumbnail
    print("\n[3/5] Generating thumbnail...")
    thumb_path = generate_thumbnail(script_path)

    # Step 4: Assemble Video
    print("\n[4/5] Assembling video...")
    video_path = assemble_video(audio_path, srt_path, script_path)

    # Step 5: Notify
    print("\n[5/5] Sending notification...")
    title = script.get("title", "Nuevo episodio")
    narrator = script.get("narrator", "?")
    hook = script.get("hook", "")

    message = (
        f"🎬 <b>Nuevo contenido listo!</b>\n\n"
        f"📝 <b>{title}</b>\n"
        f"🎙️ Narrado por: {narrator}\n"
        f"🎣 Hook: <i>{hook}</i>\n\n"
        f"📁 Archivos:\n"
        f"• Video: {os.path.basename(video_path)}\n"
        f"• Audio: {os.path.basename(audio_path)}\n"
        f"• Thumbnail: {os.path.basename(thumb_path)}\n"
        f"• Script: {os.path.basename(script_path)}\n\n"
        f"⬆️ Listo para subir a TikTok/Reels!"
    )

    notify_telegram(message, video_path, thumb_path)

    # Summary
    print("\n" + "=" * 60)
    print("  PRODUCTION COMPLETE!")
    print("=" * 60)
    print(f"  Title:     {title}")
    print(f"  Narrator:  {narrator}")
    print(f"  Video:     {video_path}")
    print(f"  Audio:     {audio_path}")
    print(f"  Thumbnail: {thumb_path}")
    print(f"  Script:    {script_path}")
    print("=" * 60)

    return {
        "script": script_path,
        "audio": audio_path,
        "subtitles": srt_path,
        "video": video_path,
        "thumbnail": thumb_path,
    }


if __name__ == "__main__":
    theme = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    asyncio.run(produce(theme))
