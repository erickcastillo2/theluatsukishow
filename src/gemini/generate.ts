#!/usr/bin/env ts-node
/**
 * Gemini Media Generator — The Lua Tsuki Show
 *
 * Genera imágenes (Imagen 3) y videos (Veo 2) usando Google Gemini API.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * GUARDA DE SEGURIDAD ANTI-DERROCHE DE API
 * ─────────────────────────────────────────────────────────────────────────────
 * Este script REQUIERE el flag --telegram para ejecutarse.
 * Sin él, sale inmediatamente con código 2.
 *
 * Propósito: evitar que OpenClaw consuma la API de Gemini durante heartbeats,
 * tareas cron, o cualquier ciclo idle. Solo se debe invocar como respuesta
 * DIRECTA a un mensaje de Telegram de un usuario real.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * USAGE
 * ─────────────────────────────────────────────────────────────────────────────
 * Image:
 *   ts-node src/gemini/generate.ts --telegram --type image \
 *     --prompt "Lua y Tsuki jugando en el parque, estilo fotografía" \
 *     [--ref /path/to/reference.jpg] [--ratio 9:16] [--prefix lua-tsuki]
 *
 * Video:
 *   ts-node src/gemini/generate.ts --telegram --type video \
 *     --prompt "Lua y Tsuki corriendo en cámara lenta, estilo cinemático" \
 *     [--ref /path/to/reference.jpg] [--ratio 9:16] [--prefix lua-video]
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * ENV VARS REQUIRED
 * ─────────────────────────────────────────────────────────────────────────────
 *   GEMINI_API_KEY  — Google AI Studio API key
 *
 * Output en: ~/.openclaw/workspace/out/
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { GoogleGenAI } from '@google/genai';
import type { GenerateOptions, GenerateResult, AspectRatio } from './types';
import { buildPrompt, BEST_REFERENCE_PHOTO } from './context';

// ─────────────────────────────────────────────────────────────────────────────
// GUARDA: verificar flag --telegram ANTES de cualquier inicialización de API
// ─────────────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);

if (!args.includes('--telegram')) {
  console.error(
    '\n[GEMINI GUARD] ❌ Bloqueado — el flag --telegram no fue pasado.\n' +
    '  Este script solo se ejecuta en respuesta a mensajes de Telegram.\n' +
    '  NO llamar durante heartbeat, cron, o ciclos idle de OpenClaw.\n' +
    '  Uso: ts-node src/gemini/generate.ts --telegram --type image|video --prompt "..."\n'
  );
  process.exit(2);
}

// ─────────────────────────────────────────────────────────────────────────────
// Parsear argumentos CLI
// ─────────────────────────────────────────────────────────────────────────────
function getArg(flag: string): string | undefined {
  const idx = args.indexOf(flag);
  return idx !== -1 ? args[idx + 1] : undefined;
}

function getFlag(flag: string): boolean {
  return args.includes(flag);
}

const type = (getArg('--type') ?? 'image') as 'image' | 'video';
const prompt = getArg('--prompt');
const ratio = (getArg('--ratio') ?? '9:16') as AspectRatio;
// Si no se pasa --ref, usa la mejor foto de referencia de Lua y Tsuki por defecto
const refPath = getArg('--ref') ?? (fs.existsSync(BEST_REFERENCE_PHOTO) ? BEST_REFERENCE_PHOTO : undefined);
const prefix = getArg('--prefix') ?? `gemini-${type}`;
const outputDir = getArg('--out') ?? path.join(os.homedir(), '.openclaw', 'workspace', 'out');

if (!prompt) {
  console.error('[GEMINI] ❌ Se requiere --prompt "descripción del contenido"');
  process.exit(1);
}

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) {
  console.error(
    '[GEMINI] ❌ Variable de entorno GEMINI_API_KEY no configurada.\n' +
    '  Configúrala en ~/.openclaw/credentials o en tu ~/.zshrc:\n' +
    '  export GEMINI_API_KEY=tu_clave_de_google_ai_studio'
  );
  process.exit(1);
}

// ─────────────────────────────────────────────────────────────────────────────
// Utilidades
// ─────────────────────────────────────────────────────────────────────────────
function ensureDir(dir: string): void {
  fs.mkdirSync(dir, { recursive: true });
}

function timestamp(): string {
  return new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ─────────────────────────────────────────────────────────────────────────────
// Cliente Gemini
// ─────────────────────────────────────────────────────────────────────────────
const ai = new GoogleGenAI({ apiKey });

// ─────────────────────────────────────────────────────────────────────────────
// Generación de IMÁGENES — Imagen 3
// ─────────────────────────────────────────────────────────────────────────────
async function generateImage(opts: GenerateOptions): Promise<GenerateResult> {
  const finalPrompt = buildPrompt(opts.prompt);
  console.log(`[GEMINI IMAGE] Generando imagen con Imagen 3...`);
  console.log(`  Prompt: ${opts.prompt}`);
  console.log(`  Ratio: ${opts.aspectRatio ?? '9:16'}`);
  if (opts.referenceImagePath) console.log(`  Referencia: ${opts.referenceImagePath}`);

  ensureDir(opts.outputDir!);

  const response = await ai.models.generateImages({
    model: 'imagen-3.0-generate-002',
    prompt: finalPrompt,
    config: {
      numberOfImages: opts.numberOfImages ?? 1,
      aspectRatio: opts.aspectRatio ?? '9:16',
      outputMimeType: 'image/jpeg',
    },
  });

  const outputPaths: string[] = [];

  for (let i = 0; i < (response.generatedImages?.length ?? 0); i++) {
    const imgData = response.generatedImages![i].image?.imageBytes;
    if (!imgData) continue;

    const filename = `${opts.outputPrefix ?? 'gemini-image'}-${timestamp()}-${i + 1}.jpg`;
    const outPath = path.join(opts.outputDir!, filename);
    fs.writeFileSync(outPath, Buffer.from(imgData as string, 'base64'));
    outputPaths.push(outPath);
    console.log(`  ✅ Imagen guardada: ${outPath}`);
  }

  return {
    success: outputPaths.length > 0,
    outputPaths,
    model: 'imagen-3.0-generate-002',
    type: 'image',
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Generación de VIDEO — Veo 2
// ─────────────────────────────────────────────────────────────────────────────
async function generateVideo(opts: GenerateOptions): Promise<GenerateResult> {
  const finalPrompt = buildPrompt(opts.prompt);
  console.log(`[GEMINI VIDEO] Generando video con Veo 2...`);
  console.log(`  Prompt: ${opts.prompt}`);
  console.log(`  Ratio: ${opts.aspectRatio ?? '9:16'}`);
  if (opts.referenceImagePath) console.log(`  Imagen referencia (image-to-video): ${opts.referenceImagePath}`);
  console.log(`  ⏳ Veo 2 tarda ~2-3 min en generar. Esperando resultado...`);

  ensureDir(opts.outputDir!);

  // Construir config base
  const config: Record<string, unknown> = {
    aspectRatio: opts.aspectRatio ?? '9:16',
    numberOfVideos: 1,
  };

  // Si hay imagen de referencia, usar image-to-video
  let image: Record<string, unknown> | undefined;
  if (opts.referenceImagePath) {
    const absRef = path.resolve(opts.referenceImagePath);
    if (!fs.existsSync(absRef)) {
      throw new Error(`Imagen de referencia no encontrada: ${absRef}`);
    }
    const imageBytes = fs.readFileSync(absRef).toString('base64');
    const ext = path.extname(absRef).toLowerCase();
    const mimeType = ext === '.png' ? 'image/png' : 'image/jpeg';
    image = { imageBytes, mimeType };
  }

  // Iniciar operación de generación (long-running)
  const operation = await ai.models.generateVideos({
    model: 'veo-2.0-generate-preview',
    prompt: finalPrompt,
    ...(image ? { image } : {}),
    config,
  });

  // Polling hasta que la operación complete
  let result = await ai.operations.getVideosOperation({ operation });
  let attempts = 0;
  const maxAttempts = 30; // ~5 min timeout (30 x 10s)

  while (!result.done && attempts < maxAttempts) {
    process.stdout.write('.');
    await sleep(10_000);
    result = await ai.operations.getVideosOperation({ operation });
    attempts++;
  }
  process.stdout.write('\n');

  if (!result.done) {
    throw new Error(`Timeout: Veo 2 no completó en ${maxAttempts * 10}s`);
  }

  const outputPaths: string[] = [];
  const generatedVideos = result.response?.generatedVideos ?? [];

  for (let i = 0; i < generatedVideos.length; i++) {
    const videoData = generatedVideos[i].video?.videoBytes;
    if (!videoData) continue;

    const filename = `${opts.outputPrefix ?? 'gemini-video'}-${timestamp()}-${i + 1}.mp4`;
    const outPath = path.join(opts.outputDir!, filename);
    fs.writeFileSync(outPath, Buffer.from(videoData as string, 'base64'));
    outputPaths.push(outPath);
    console.log(`  ✅ Video guardado: ${outPath}`);
  }

  return {
    success: outputPaths.length > 0,
    outputPaths,
    model: 'veo-2.0-generate-preview',
    type: 'video',
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────────────────────────────────────
async function main(): Promise<void> {
  const opts: GenerateOptions = {
    telegramTrigger: true, // ya validado arriba con el guard
    type,
    prompt: prompt!,
    aspectRatio: ratio,
    referenceImagePath: refPath,
    outputDir,
    outputPrefix: prefix,
    numberOfImages: 1,
  };

  let result: GenerateResult;

  if (type === 'image') {
    result = await generateImage(opts);
  } else if (type === 'video') {
    result = await generateVideo(opts);
  } else {
    console.error(`[GEMINI] ❌ Tipo inválido: ${type}. Usa --type image o --type video`);
    process.exit(1);
  }

  if (!result.success) {
    console.error('[GEMINI] ❌ Generación fallida — sin archivos de salida.');
    process.exit(1);
  }

  console.log(`\n[GEMINI] ✅ Listo! ${result.outputPaths.length} archivo(s) generado(s):`);
  result.outputPaths.forEach(p => console.log(`  → ${p}`));
}

main().catch(err => {
  console.error('[GEMINI] ❌ Error fatal:', err instanceof Error ? err.message : err);
  process.exit(1);
});
