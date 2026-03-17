# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Setup específico — The Lua Tsuki Show

### FFmpeg
- Binario: `~/ai-local/ffmpeg` (symlink en `~/bin/ffmpeg`)
- Output dir: `~/.openclaw/workspace/out/`
- Inbound media: `~/.openclaw/media/inbound/`

### TTS
- Herramientas: `edge-tts`, `gTTS`, `pydub`
- Voz preferida: español natural (`edge-tts es-MX-DaliaNeural`)

### Google Gemini
- Paquete: `@google/genai` (instalado en el repo)
- Script: `ts-node src/gemini/generate.ts`
- API Key: env var `GEMINI_API_KEY` (configurar en `~/.zshrc` o credenciales de OpenClaw)
- Modelos:
  - Imágenes: `imagen-3.0-generate-002`
  - Videos: `veo-2.0-generate-preview` (clips de ~5-8s)
- **GUARD OBLIGATORIO**: siempre pasar `--telegram` — sin él el script aborta (exit 2)
- **REGLA**: solo llamar Gemini cuando hay un mensaje real de Telegram esperando respuesta

### Los perros del show
- **Lua** — pelaje claro/dorado (usualmente a la izquierda en fotos de pareja)
- **Tsuki** — pelaje más oscuro/café (usualmente a la derecha)
- Siempre mencionar ambas en los prompts para coherencia de marca

### Prompts de referencia para Gemini

**Imagen vertical (Reels/TikTok):**
```
Dos perros adorables, Lua (golden) y Tsuki (café), [acción], fondo [descripción],
fotografía profesional estilo Instagram, iluminación natural, colores vibrantes, 9:16
```

**Video (Veo 2):**
```
Two cute dogs, one golden (Lua) and one brown (Tsuki), [action], [location],
cinematic slow motion, natural light, social media vertical format
```

Add whatever helps you do your job. This is your cheat sheet.
