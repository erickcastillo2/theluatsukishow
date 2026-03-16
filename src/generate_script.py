#!/usr/bin/env python3
"""
Story Script Generator for The Lua Tsuki Show.
Uses OpenRouter API (Qwen) to generate entertaining stories
narrated by Lua and Tsuki, two dachshund dogs.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import random
from datetime import datetime

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENCLAW_PASSWORD = os.environ.get("OPENCLAW_GATEWAY_PASSWORD", "")
OPENCLAW_PORT = os.environ.get("OPENCLAW_PORT", "18789")
MODELS = [
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-27b-it:free",
    "microsoft/phi-4-reasoning:free",
]
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content", "scripts")

STORY_THEMES = [
    "Una aventura en el parque donde Lua y Tsuki encuentran algo inesperado",
    "Tsuki intenta robar comida de la cocina mientras Lua vigila",
    "Las perritas descubren un misterio en el jardín del vecino",
    "Lua y Tsuki compiten por ver quién es la más consentida",
    "Un día lluvioso donde las perritas inventan un juego dentro de casa",
    "Las perritas se escapan al supermercado y causan caos",
    "Lua le cuenta a Tsuki una historia de terror (versión perrita)",
    "Las perritas intentan cocinar algo para sus humanos",
    "Tsuki descubre su reflejo en el espejo y cree que es otra perrita",
    "Lua y Tsuki planean una fiesta sorpresa para su humano",
    "Las perritas van al veterinario y hacen un plan de escape",
    "Un gato nuevo en el vecindario desafía a Lua y Tsuki",
    "Las perritas descubren qué hay debajo del sillón",
    "Lua y Tsuki se hacen influencers por un día",
    "Las perritas encuentran un tesoro enterrado en el patio",
]

SYSTEM_PROMPT = """Eres el guionista principal de "The Lua Tsuki Show", un canal de entretenimiento protagonizado por dos perritas salchicha (dachshund): Lua y Tsuki.

REGLAS DEL GUIÓN:
- El guión es para un video corto de TikTok/Reels (60-90 segundos de narración)
- Debe tener entre 150-250 palabras
- Narrado en primera persona por Lua (la más grande y sabia) o Tsuki (la más traviesa y curiosa)
- Tono: divertido, tierno, con humor sarcástico tipo stand-up
- Incluye acotaciones breves entre [corchetes] para indicar acciones o emociones
- Estructura: gancho inicial (5 seg), desarrollo divertido, remate/punchline
- El público objetivo son amantes de perros y comedia
- Idioma: español latino, informal, expresivo
- NO uses hashtags ni emojis en el guión

FORMATO DE SALIDA (JSON):
{
  "title": "Título corto y llamativo del episodio",
  "narrator": "Lua" o "Tsuki",
  "hook": "Primera frase gancho que atrapa la atención",
  "script": "El guión completo con acotaciones entre [corchetes]",
  "thumbnail_text": "Texto corto para la miniatura (máx 5 palabras)",
  "tags": ["tag1", "tag2", "tag3"]
}

Responde SOLO con el JSON, sin texto adicional."""


def generate_script(theme=None):
    """Generate a story script using OpenClaw gateway (Copilot) or OpenRouter."""
    if not OPENROUTER_API_KEY and not OPENCLAW_PASSWORD:
        print("ERROR: Set OPENROUTER_API_KEY or OPENCLAW_GATEWAY_PASSWORD")
        sys.exit(1)

    if theme is None:
        theme = random.choice(STORY_THEMES)

    print(f"Generating script for theme: {theme}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Escribe un guión sobre: {theme}"}
    ]

    data = None

    # Try 1: OpenClaw gateway (GitHub Copilot)
    if OPENCLAW_PASSWORD:
        print("Trying OpenClaw gateway (GitHub Copilot)...")
        payload = json.dumps({
            "model": "github-copilot/gpt-5.2",
            "messages": messages,
            "temperature": 0.9,
            "max_tokens": 1000
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://localhost:{OPENCLAW_PORT}/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENCLAW_PASSWORD}",
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            print("Using: GitHub Copilot via OpenClaw")
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            err_msg = str(e)
            if hasattr(e, 'read'):
                err_msg = e.read().decode("utf-8", errors="replace")
            print(f"OpenClaw gateway failed: {err_msg[:200]}")

    # Try 2: OpenRouter (free models with retry)
    if not data and OPENROUTER_API_KEY:
        print("Falling back to OpenRouter...")
        model_from_env = os.environ.get("AI_MODEL", "")
        models_to_try = [model_from_env] if model_from_env else MODELS

        for model in models_to_try:
            for attempt in range(3):
                payload = json.dumps({
                    "model": model,
                    "messages": messages,
                    "temperature": 0.9,
                    "max_tokens": 1000
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    }
                )
                try:
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    print(f"Using model: {model}")
                    break
                except urllib.error.HTTPError as e:
                    body = e.read().decode("utf-8", errors="replace")
                    if e.code == 429:
                        wait = (attempt + 1) * 10
                        print(f"Rate limited on {model}, waiting {wait}s... (attempt {attempt+1}/3)")
                        time.sleep(wait)
                    elif e.code == 404:
                        print(f"Model {model} not found, trying next...")
                        break
                    else:
                        print(f"API Error {e.code}: {body}")
                        break
            if data:
                break

    if not data:
        print("ERROR: All providers failed. Try again later.")
        sys.exit(1)

    content = data["choices"][0]["message"]["content"]

    # Clean markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]
    content = content.strip()

    try:
        script = json.loads(content)
    except json.JSONDecodeError:
        print("Warning: AI response was not valid JSON, saving raw text")
        script = {"raw": content, "title": "untitled", "script": content}

    # Save script
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = script.get("title", "untitled").replace(" ", "_")[:30]
    filename = f"{timestamp}_{safe_title}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    print(f"Script saved: {filepath}")
    print(f"Title: {script.get('title', 'N/A')}")
    print(f"Narrator: {script.get('narrator', 'N/A')}")
    print(f"Hook: {script.get('hook', 'N/A')}")
    word_count = len(script.get("script", "").split())
    print(f"Words: {word_count}")

    return filepath, script


if __name__ == "__main__":
    theme = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    generate_script(theme)
