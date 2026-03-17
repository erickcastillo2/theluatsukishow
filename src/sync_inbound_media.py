#!/usr/bin/env python3
"""
Sync Telegram media downloaded by OpenClaw into the repo content folders.

OpenClaw already stores inbound attachments under ~/.openclaw/media/inbound.
This script mirrors those files into the repo paths that the CEO and the rest
of the content pipeline expect to use.
"""

import shutil
import sys
import time
from pathlib import Path
from typing import Optional, Tuple


BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = Path.home() / '.openclaw' / 'media' / 'inbound'
PHOTOS_DIR = BASE_DIR / 'content' / 'fotos' / 'telegram'
VIDEOS_DIR = BASE_DIR / 'content' / 'videos' / 'telegram'
DOCS_DIR = BASE_DIR / 'content' / 'docs' / 'telegram'

PHOTO_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
VIDEO_EXTS = {'.mp4', '.mov', '.m4v', '.avi', '.webm'}
DOC_EXTS = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.zip'}


def ensure_dirs() -> None:
    for directory in (PHOTOS_DIR, VIDEOS_DIR, DOCS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def classify_destination(file_path: Path) -> Optional[Path]:
    suffix = file_path.suffix.lower()
    if suffix in PHOTO_EXTS:
        return PHOTOS_DIR
    if suffix in VIDEO_EXTS:
        return VIDEOS_DIR
    if suffix in DOC_EXTS:
        return DOCS_DIR
    return None


def sync_once() -> Tuple[int, int]:
    ensure_dirs()
    if not SOURCE_DIR.exists():
        return 0, 0

    copied = 0
    skipped = 0

    for source_file in sorted(SOURCE_DIR.iterdir()):
        if not source_file.is_file():
            continue

        destination_dir = classify_destination(source_file)
        if destination_dir is None:
            skipped += 1
            continue

        destination_file = destination_dir / source_file.name
        if destination_file.exists():
            continue

        shutil.copy2(source_file, destination_file)
        copied += 1

    return copied, skipped


def main() -> int:
    watch = '--watch' in sys.argv

    if watch:
        print(f'Syncing inbound Telegram media from {SOURCE_DIR}')
        print(f'Photos -> {PHOTOS_DIR}')
        print(f'Videos -> {VIDEOS_DIR}')
        print(f'Docs   -> {DOCS_DIR}')
        while True:
            copied, skipped = sync_once()
            if copied:
                print(f'Copied {copied} file(s); skipped {skipped} unknown file(s)')
            time.sleep(60)

    copied, skipped = sync_once()
    print(f'Copied {copied} file(s); skipped {skipped} unknown file(s)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())