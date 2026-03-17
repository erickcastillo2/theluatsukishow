/**
 * Contexto de marca para The Lua Tsuki Show.
 * Este módulo provee el system prompt que se prepend automáticamente
 * a cada llamada a Gemini (Imagen 3 / Veo 2), para que la IA siempre
 * sepa de qué trata el proyecto y quiénes son los personajes.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

// ─────────────────────────────────────────────────────────────────────────────
// Brief del proyecto
// ─────────────────────────────────────────────────────────────────────────────
export const BRAND_CONTEXT = `
The Lua Tsuki Show es una marca de contenido en redes sociales protagonizada por
dos perras: Lua (pelaje negro) y Tsuki (pelaje naranja/cafe). Son hermanas
y conviven juntas. El contenido es en español, cálido, divertido y profesional.
Plataformas: Instagram, TikTok, Facebook.

Personajes:
- Lua: negra, más extrovertida, suele aparecer a la izquierda.
- Tsuki: naranja/cafe, más tranquila, suele aparecer a la derecha.

Tipos de contenido permitidos:
1. Mejora de fotos reales (más luz, colores vibrantes, fondo limpio).
2. Imágenes cómicas con contexto gracioso o memes caninos.
3. Videos cortos cómicos (situaciones absurdas cotidianas de perros).
4. Videos narrando historias de Reddit desde la perspectiva de Lua y Tsuki.

Estética: fotografía de mascota profesional, colores cálidos y vibrantes,
estilo Instagram/TikTok, sin texto superpuesto, enfoque en las caras expresivas
de los perros. Siempre 9:16 excepto que se indique lo contrario.

NO incluir: personas humanas prominentes, marcas comerciales, violencia, texto
en la imagen (a menos que se pida explícitamente).
`.trim();

// ─────────────────────────────────────────────────────────────────────────────
// Imágenes de referencia disponibles (fotos reales de Lua y Tsuki)
// ─────────────────────────────────────────────────────────────────────────────
export const INBOUND_DIR = path.join(os.homedir(), '.openclaw', 'media', 'inbound');
export const TELEGRAM_PHOTOS_DIR = path.join(
  path.resolve(__dirname, '..', '..'),
  'content',
  'fotos',
  'telegram'
);

const BEST_REFERENCE_NAME = 'file_47---6eb42dfd-2d30-4b62-97e0-9dc1f526efea.jpg';

/**
 * Foto de referencia recomendada: la que mejor muestra a las dos juntas
 * (file_47 fue identificada como la mejor foto de pareja en sesiones anteriores).
 */
export const BEST_REFERENCE_PHOTO = [
  path.join(TELEGRAM_PHOTOS_DIR, BEST_REFERENCE_NAME),
  path.join(INBOUND_DIR, BEST_REFERENCE_NAME),
].find(candidate => fs.existsSync(candidate)) ?? path.join(INBOUND_DIR, BEST_REFERENCE_NAME);

/**
 * Construye el prompt final para Gemini: brand context + prompt del usuario.
 * Evita que el agente tenga que repetir el contexto en cada llamada.
 */
export function buildPrompt(userPrompt: string, includeBrandContext = true): string {
  if (!includeBrandContext) return userPrompt;
  return `${BRAND_CONTEXT}\n\n---\n\nPetición específica: ${userPrompt}`;
}
