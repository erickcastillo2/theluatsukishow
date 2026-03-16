# 🐕 The Lua Tsuki Show

Canal de contenido protagonizado por **Lua** y **Tsuki**, dos perritas que narran historias, cuentan chismes de Reddit y crean contenido para redes sociales — todo gestionado por un equipo de agentes AI.

## El Equipo

| Emoji | Agente | Rol |
|-------|--------|-----|
| 👔 | **CEO** | Director General. Se comunica con los dueños por Telegram, aprueba contenido y coordina al equipo |
| 📋 | **Scrum Master** | Organiza sprints semanales, asigna tareas y da seguimiento |
| 📱 | **Community Manager** | Publica en Instagram, Facebook y TikTok. Gestiona audiencia |
| 🎨 | **Content Designer** | Diseña propuestas de contenido: fotos, videos, reels, thumbnails |
| 💻 | **Programmer** | Crea videos interactivos donde Lua y Tsuki narran historias de Reddit |
| 🎬 | **AV Engineer** | Edición de audio y video, post-producción, mezcla y exportación |

## Estructura del Proyecto

```
theluatsukishow/
├── agents/                          # Workspaces de cada agente
│   ├── ceo/IDENTITY.md
│   ├── community-manager/IDENTITY.md
│   ├── content-designer/IDENTITY.md
│   ├── programmer/IDENTITY.md
│   ├── scrum-master/IDENTITY.md
│   └── av-engineer/IDENTITY.md
├── content/                         # Material de producción
│   ├── fotos/{lua, tsuki, juntas}   # Fotos de las perritas
│   ├── videos/
│   │   ├── raw/                     # Videos sin editar
│   │   ├── editados/                # Videos finales
│   │   ├── thumbnails/              # Miniaturas
│   │   └── propuestas/              # Propuestas para aprobación
│   ├── audio/                       # Narraciones y música
│   └── scripts/                     # Guiones de historias de Reddit
├── assets/                          # Branding
│   ├── templates/
│   ├── logos/
│   └── fonts/
├── src/                             # Código de la aplicación
└── config/                          # Configuración adicional
```

## Miniverse — Oficina Pixel Art

Los agentes tienen una representación visual en **[Miniverse](https://www.minivrs.com/)**, un mundo pixel art donde puedes ver al equipo trabajando en tiempo real.

### Instalar Miniverse

```bash
npx create-miniverse
cd my-miniverse
npm run dev
```

Abre el URL de Vite en tu navegador y verás la oficina con los 6 agentes como ciudadanos pixel art.

### Cómo funciona

| Evento | Estado | Visual |
|--------|--------|--------|
| Gateway arranca | idle | El agente aparece y pasea |
| Recibe mensaje | thinking | Camina al escritorio, burbujas de pensamiento |
| Envía respuesta | idle | Vuelve a pasear |
| Se detiene | offline | El agente desaparece |

### Conectar OpenClaw con Miniverse

1. Crear el hook en `~/.openclaw/hooks/miniverse/`
2. Configurar `MINIVERSE_URL=http://localhost:4321`
3. Habilitar: `openclaw hooks enable miniverse`
4. Reiniciar gateway: `openclaw gateway restart`

Ver la [documentación de Miniverse para OpenClaw](https://www.minivrs.com/docs/#openclaw-quickstart) para la guía completa.

## Flujo de Trabajo

```
Dueños (Telegram) ──→ 👔 CEO ──→ 📋 Scrum Master ──→ Asigna tareas
                                                      ├── 🎨 Content Designer
                                                      ├── 📱 Community Manager
                                                      ├── 💻 Programmer
                                                      └── 🎬 AV Engineer
```

1. **CEO** pide fotos/videos de Lua y Tsuki a los dueños por Telegram
2. **Content Designer** propone qué tipo de contenido crear
3. **Programmer** + **AV Engineer** producen videos interactivos
4. **CEO** presenta propuestas en Telegram para aprobación
5. **Community Manager** publica el contenido aprobado

## Videos Interactivos — Chismes de Reddit

El Programmer crea videos donde miniaturas de Lua y Tsuki narran historias populares de Reddit:

- Scraping de historias con **PRAW** (Reddit API)
- Narración con **edge-tts** (Text-to-Speech)
- Composición con **MoviePy** + **FFmpeg**
- Post-producción con el **AV Engineer**
- Edición adicional con **CapCut**

## Tech Stack

- **OpenClaw** — Orquestación de agentes AI
- **Qwen3-Next-80B** — Modelo LLM (OpenRouter, gratuito)
- **Miniverse** — Visualización pixel art de agentes
- **FFmpeg 8.0.1** — Procesamiento de video
- **Python 3.9** — Pillow, MoviePy, PRAW, gTTS, edge-tts, pydub
- **Node.js 24** — Runtime
- **CapCut** — Edición de fotos y video
- **Telegram** — Canal de comunicación con los dueños

## Bot de Telegram

**@ceo_theluatsukishow_bot** — El CEO del equipo. Envía mensajes al grupo de Telegram para:
- Pedir material (fotos, videos de Lua y Tsuki)
- Presentar propuestas de contenido para aprobación
- Reportar avances del equipo
- Solicitar credenciales de redes sociales

## Licencia

MIT

3. **Compile TypeScript**
   To compile the TypeScript files, run:
   ```bash
   npm run build
   ```

4. **Run the Application**
   To start the application, use:
   ```bash
   npm start
   ```

## Usage
After starting the application, you can access it at `http://localhost:3000`. Follow the on-screen instructions to interact with the application.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.