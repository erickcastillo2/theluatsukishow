#!/usr/bin/env python3
"""
Narration Generator for The Lua Tsuki Show.
Converts story scripts to audio using Microsoft Edge TTS.
Lua gets a warm female voice, Tsuki gets a younger/playful female voice.
"""

import asyncio
import json
import os
import re
import sys

import edge_tts

# Spanish (Mexico) voices
VOICES = {
    "Lua": "es-MX-DaliaNeural",      # Warm, mature female
    "Tsuki": "es-MX-BeatrizNeural",   # Younger, playful female (fallback: es-MX-DaliaNeural with pitch shift)
}
# Fallback if BeatrizNeural not available
FALLBACK_VOICE = "es-MX-DaliaNeural"

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content", "audio")


def clean_script_for_tts(script_text):
    """Remove stage directions [brackets] and clean text for TTS."""
    # Remove content in brackets (stage directions)
    cleaned = re.sub(r'\[.*?\]', '...', script_text)
    # Remove multiple dots/spaces
    cleaned = re.sub(r'\.{3,}', '...', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


async def generate_narration(script_path):
    """Generate audio narration from a script JSON file."""
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    narrator = script.get("narrator", "Lua")
    voice = VOICES.get(narrator, FALLBACK_VOICE)
    script_text = script.get("script", "")

    if not script_text:
        print("ERROR: Script has no text")
        sys.exit(1)

    cleaned_text = clean_script_for_tts(script_text)
    print(f"Narrator: {narrator} (voice: {voice})")
    print(f"Text length: {len(cleaned_text)} chars")

    os.makedirs(AUDIO_DIR, exist_ok=True)

    # Output filename based on script filename
    base_name = os.path.splitext(os.path.basename(script_path))[0]
    audio_path = os.path.join(AUDIO_DIR, f"{base_name}.mp3")
    srt_path = os.path.join(AUDIO_DIR, f"{base_name}.srt")

    # Generate audio with subtitles
    communicate = edge_tts.Communicate(
        cleaned_text,
        voice,
        rate="+5%",   # Slightly faster for energy
        pitch="+10Hz" if narrator == "Tsuki" else "+0Hz"  # Higher pitch for Tsuki
    )

    sentences = []
    with open(audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                sentences.append(chunk)

    # Generate SRT from sentence/word boundaries
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        for i, sent in enumerate(sentences):
            offset = sent["offset"]  # in 100-nanosecond ticks
            duration = sent["duration"]
            text = sent.get("text", "")
            if not text:
                continue
            start_time = format_srt_time(offset)
            end_time = format_srt_time(offset + duration)
            srt_file.write(f"{i+1}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")

    print(f"Audio saved: {audio_path}")
    print(f"Subtitles saved: {srt_path}")
    file_size = os.path.getsize(audio_path)
    print(f"Audio size: {file_size / 1024:.1f} KB")

    return audio_path, srt_path


def format_srt_time(ticks):
    """Convert 100-nanosecond ticks to SRT timestamp."""
    ms = ticks / 10000
    hours = int(ms // 3600000)
    ms %= 3600000
    minutes = int(ms // 60000)
    ms %= 60000
    seconds = int(ms // 1000)
    ms %= 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{int(ms):03d}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_narration.py <script.json>")
        sys.exit(1)

    asyncio.run(generate_narration(sys.argv[1]))
