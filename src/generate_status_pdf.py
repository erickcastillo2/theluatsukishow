#!/usr/bin/env python3
"""
Generate a PDF status report for The Lua Tsuki Show team.
Shows agent info, recent content, and system status.
Zero AI tokens consumed.

Usage:
  python3 generate_status_pdf.py          # Generate PDF only
  python3 generate_status_pdf.py --send   # Generate and send to Telegram
"""

import glob
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUTPUT_DIR = os.path.join(BASE_DIR, "content", "reports")

AGENTS = [
    ("CEO", "Coordinador general, puente Telegram", "main"),
    ("Community Manager", "Redes sociales, engagement", "community-manager"),
    ("Content Designer", "Guiones, storytelling", "content-designer"),
    ("Programmer", "Automatizacion, scripts", "programmer"),
    ("Scrum Master", "Tareas, sprints, seguimiento", "scrum-master"),
    ("AV Engineer", "Audio, video, edicion", "av-engineer"),
]


def check_process(name):
    try:
        out = subprocess.check_output(["pgrep", "-f", name], text=True).strip()
        return "Activo" if out else "Inactivo"
    except subprocess.CalledProcessError:
        return "Inactivo"


def count_files(directory, extensions):
    total = 0
    for ext in extensions:
        total += len(glob.glob(os.path.join(directory, "**", f"*{ext}"), recursive=True))
    return total


def get_recent_files(directory, extensions, limit=5):
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(directory, "**", f"*{ext}"), recursive=True))
    files.sort(key=os.path.getmtime, reverse=True)
    result = []
    for f in files[:limit]:
        mtime = datetime.fromtimestamp(os.path.getmtime(f))
        result.append((os.path.basename(f), mtime.strftime("%Y-%m-%d %H:%M")))
    return result


def generate_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now()
    filename = f"status_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    NL = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}
    SM = {"new_x": XPos.RIGHT, "new_y": YPos.TOP}

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "The Lua Tsuki Show", align="C", **NL)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Reporte de Estado - {now.strftime('%d/%m/%Y %H:%M')}", align="C", **NL)
    pdf.ln(8)

    # System Status
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "  Estado del Sistema", fill=True, **NL)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)

    openclaw_status = check_process("openclaw-gateway")
    miniverse_status = check_process("miniverse")
    caffeinate_status = check_process("caffeinate")

    systems = [
        ("OpenClaw Gateway", openclaw_status),
        ("Miniverse Server", miniverse_status),
        ("Caffeinate (anti-sleep)", caffeinate_status),
    ]
    for name, status in systems:
        color = (0, 128, 0) if status == "Activo" else (200, 0, 0)
        pdf.cell(90, 7, f"  {name}:", **SM)
        pdf.set_text_color(*color)
        pdf.cell(0, 7, status, **NL)
        pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # Agents
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "  Equipo de Agentes", fill=True, **NL)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)

    for name, role, agent_id in AGENTS:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(55, 7, f"  {name}", **SM)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 7, role, **NL)
        pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # Content Stats
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "  Contenido Generado", fill=True, **NL)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)

    content_dir = os.path.join(BASE_DIR, "content")
    stats = [
        ("Guiones", count_files(os.path.join(content_dir, "scripts"), [".json"])),
        ("Audios/Narraciones", count_files(os.path.join(content_dir, "audio"), [".mp3", ".wav"])),
        ("Videos", count_files(os.path.join(content_dir, "videos"), [".mp4", ".mov"])),
        ("Fotos/Thumbnails", count_files(os.path.join(content_dir, "fotos"), [".jpg", ".png", ".jpeg"])),
        ("Fotos Telegram", count_files(os.path.join(content_dir, "fotos", "telegram"), [".jpg", ".png", ".jpeg"])),
        ("Videos Telegram", count_files(os.path.join(content_dir, "videos", "telegram"), [".mp4", ".mov"])),
    ]
    for label, count in stats:
        pdf.cell(90, 7, f"  {label}:", **SM)
        pdf.cell(0, 7, str(count), **NL)
    pdf.ln(4)

    # Recent Files
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "  Archivos Recientes", fill=True, **NL)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)

    recent = get_recent_files(content_dir, [".json", ".mp3", ".mp4", ".png", ".jpg", ".srt"], limit=8)
    if recent:
        for fname, mtime in recent:
            pdf.cell(120, 6, f"  {fname[:50]}", **SM)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 6, mtime, **NL)
            pdf.set_text_color(0, 0, 0)
    else:
        pdf.cell(0, 7, "  Sin archivos recientes", **NL)

    pdf.ln(6)

    # Footer
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, "Generado automaticamente - sin consumo de tokens IA", align="C", **NL)
    pdf.cell(0, 6, f"The Lua Tsuki Show - {now.strftime('%Y')}", align="C", **NL)

    pdf.output(filepath)
    print(filepath)
    return filepath


if __name__ == "__main__":
    path = generate_pdf()
    print(f"PDF generado: {path}")

    if "--send" in sys.argv:
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "-5106063868")
        if not token:
            print("ERROR: Set TELEGRAM_BOT_TOKEN")
            sys.exit(1)

        import mimetypes
        boundary = "----FormBoundary7MA4YWxkTrZu0gW"
        with open(path, "rb") as f:
            file_data = f.read()
        filename = os.path.basename(path)

        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="caption"\r\n\r\n'
            f"Reporte de estado (0 tokens IA)\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'
            f"Content-Type: application/pdf\r\n\r\n"
        ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendDocument",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                if result.get("ok"):
                    print("PDF enviado a Telegram OK")
                else:
                    print(f"Error Telegram: {result}")
        except urllib.error.URLError as e:
            print(f"Error enviando PDF: {e}")
