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

### CapCut (Desktop App)
- App: `/Applications/CapCut.app`
- Bundle ID: `com.lemon.lvoverseas`
- URL Scheme: `capcut://`
- Uso: Edición avanzada de video con plantillas, efectos, transiciones y texto animado
- **Abrir CapCut:**
  ```bash
  open -a CapCut
  # o con URL scheme:
  open "capcut://"
  ```
- **Abrir un archivo de video directo en CapCut:**
  ```bash
  open -a CapCut /ruta/al/video.mp4
  ```
- **Workflow recomendado:**
  1. Preparar clips con FFmpeg (recortar, redimensionar, extraer audio)
  2. Abrir en CapCut para efectos avanzados, plantillas y texto animado
  3. Exportar desde CapCut en el formato final
- **Limitaciones:** CapCut no tiene CLI de renderizado — requiere interacción GUI
- **Tip:** Prepara los assets (clips recortados, audio mezclado, subtítulos SRT) con FFmpeg antes de pasarlos a CapCut para minimizar trabajo manual

### iMovie
- App: `/Applications/iMovie.app`
- Estado: **Instalado** ✅
- Bundle ID: `com.apple.iMovieApp`
- **Abrir iMovie:**
  ```bash
  open -a iMovie
  ```
- **Abrir video en iMovie:**
  ```bash
  open -a iMovie /ruta/al/video.mp4
  ```
- **AppleScript (una vez instalado):**
  ```bash
  osascript -e 'tell application "iMovie" to activate'
  ```
- **Workflow recomendado:**
  1. Preparar clips con FFmpeg
  2. Importar en iMovie para edición con plantillas de Apple
  3. Exportar con Share → File
- **Nota:** iMovie es más limitado que CapCut pero tiene buenas plantillas de trailers

### Workflow de Producción Completo

```
Media inbound → FFmpeg (trim/resize/audio) → CapCut o iMovie (efectos/plantillas)
                                            ↓
                                    Gemini (generar nuevos assets)
                                            ↓
                              Output final → ~/.openclaw/workspace/out/
```

| Herramienta | Mejor para |
|-------------|------------|
| FFmpeg | Recortar, redimensionar, extraer audio, convertir formatos, procesamiento batch |
| CapCut | Efectos avanzados, texto animado, plantillas trendy, transiciones pro |
| iMovie | Trailers con plantillas Apple, edición simple y rápida |
| Gemini Imagen 3 | Generar fotos nuevas de Lua y Tsuki desde cero |
| Gemini Veo 2 | Generar clips de video cortos (~5-8s) |
| MoviePy | Procesamiento programático de video en Python |
| Pillow | Procesamiento de imágenes en Python |
| edge-tts | Narración TTS en español |

Add whatever helps you do your job. This is your cheat sheet.
