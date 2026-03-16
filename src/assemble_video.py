#!/usr/bin/env python3
"""
Video Assembler for The Lua Tsuki Show.
Combines audio narration + background + subtitles into a vertical video
optimized for TikTok/Reels (1080x1920, 9:16).
"""

import json
import os
import re
import shutil
import sys
import subprocess
import tempfile

FFMPEG = os.path.expanduser("~/bin/ffmpeg")
VIDEO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content", "videos")
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def get_audio_duration(audio_path):
    """Get audio duration in seconds using ffprobe."""
    ffprobe = FFMPEG.replace("ffmpeg", "ffprobe")
    if not os.path.exists(ffprobe):
        # Try ffprobe from same dir or PATH
        ffprobe = "ffprobe"

    try:
        result = subprocess.run(
            [ffprobe, "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", audio_path],
            capture_output=True, text=True, timeout=10
        )
        return float(result.stdout.strip())
    except (ValueError, subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback: estimate from file size (MP3 ~16kB/s for speech)
        size = os.path.getsize(audio_path)
        return size / 16000


def create_background_video(duration, output_path, color="#1a1a2e"):
    """Create a solid color vertical background video."""
    subprocess.run([
        FFMPEG, "-y",
        "-f", "lavfi",
        "-i", f"color=c={color}:s=1080x1920:d={duration}:r=30",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        output_path
    ], capture_output=True, timeout=120)


def assemble_video(audio_path, srt_path, script_path):
    """Assemble the final video with audio and subtitles."""
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    title = script.get("title", "Episodio")
    narrator = script.get("narrator", "Lua")

    os.makedirs(VIDEO_DIR, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(script_path))[0]
    output_path = os.path.join(VIDEO_DIR, f"{base_name}.mp4")

    duration = get_audio_duration(audio_path)
    print(f"Audio duration: {duration:.1f}s")

    # Escape special characters in paths and text for ffmpeg filters
    # Copy SRT to a temp file with ASCII-safe name to avoid ffmpeg subtitle filter issues
    tmp_dir = tempfile.mkdtemp(prefix="luatsuki_")
    tmp_srt = os.path.join(tmp_dir, "subs.srt")
    shutil.copy2(srt_path, tmp_srt)
    srt_escaped = tmp_srt.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")

    # Narrator colors
    colors = {
        "Lua": {"bg": "#2d1b69", "accent": "#f5af19", "sub_color": "&HFFFFFF&"},
        "Tsuki": {"bg": "#1b4332", "accent": "#95d5b2", "sub_color": "&HFFFFFF&"},
    }
    style = colors.get(narrator, colors["Lua"])

    # Build ffmpeg command
    # Creates vertical video with:
    # - Gradient-ish background
    # - Title text at top
    # - Subtitles in center-bottom area
    # - Audio narration

    # Title text (safe for ffmpeg)
    safe_title = re.sub(r'[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ¿¡ !?,.]', '', title)
    narrator_label = f"Narrado por {narrator}"

    filter_complex = (
        # Background gradient
        f"color=c={style['bg']}:s=1080x1920:d={duration}:r=30[bg];"
        # Top accent bar
        f"color=c={style['accent']}:s=1080x6:d={duration}:r=30[bar];"
        f"[bg][bar]overlay=0:0[v1];"
        # Title text
        f"[v1]drawtext=text='{safe_title}':"
        f"fontsize=52:fontcolor={style['accent']}:"
        f"x=(w-text_w)/2:y=180:"
        f"font=Arial:fontfile=''[v2];"
        # Narrator label
        f"[v2]drawtext=text='{narrator_label}':"
        f"fontsize=32:fontcolor=white@0.6:"
        f"x=(w-text_w)/2:y=260:"
        f"font=Arial[v3];"
        # Show logo/branding
        f"[v3]drawtext=text='The Lua Tsuki Show':"
        f"fontsize=28:fontcolor=white@0.4:"
        f"x=(w-text_w)/2:y=1850:"
        f"font=Arial[v4];"
        # Subtitles
        "[v4]subtitles='" + srt_escaped + "':"
        "force_style='FontSize=24,PrimaryColour=" + style["sub_color"] + ","
        "OutlineColour=&H000000&,Outline=2,Alignment=2,"
        "MarginV=400,FontName=Arial'[vout]"
    )

    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"color=c={style['bg']}:s=1080x1920:d={duration}:r=30",
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ]

    print(f"Assembling video: {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"FFmpeg Error:\n{result.stderr[-500:]}")
        sys.exit(1)

    shutil.rmtree(tmp_dir, ignore_errors=True)
    file_size = os.path.getsize(output_path)
    print(f"Video saved: {output_path}")
    print(f"Size: {file_size / (1024*1024):.1f} MB")
    print(f"Duration: {duration:.1f}s")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 assemble_video.py <audio.mp3> <subtitles.srt> <script.json>")
        sys.exit(1)

    assemble_video(sys.argv[1], sys.argv[2], sys.argv[3])
