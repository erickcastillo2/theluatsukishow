/**
 * Types for the Gemini media generation pipeline.
 * Covers Imagen 3 (images) and Veo 2 (video) via @google/genai.
 */

export type GenerationType = 'image' | 'video';

export type AspectRatio =
  | '1:1'   // Instagram post
  | '9:16'  // TikTok / Instagram Reels / Stories
  | '16:9'  // Facebook / YouTube
  | '4:3';

export interface GenerateOptions {
  /** Must be true — script refuses to run without a Telegram trigger. */
  telegramTrigger: boolean;

  type: GenerationType;

  /** Text prompt describing what to generate. */
  prompt: string;

  /** Aspect ratio for the output. Defaults to 9:16 for vertical social content. */
  aspectRatio?: AspectRatio;

  /**
   * Optional reference image path (absolute or relative to cwd).
   * For image generation: used as style reference via Imagen edit mode.
   * For video generation: image-to-video with Veo 2.
   */
  referenceImagePath?: string;

  /** Number of images to generate (image type only, 1–4). Defaults to 1. */
  numberOfImages?: number;

  /** Where to save the output file. Defaults to ~/.openclaw/workspace/out/ */
  outputDir?: string;

  /** Optional filename prefix for the output file. */
  outputPrefix?: string;
}

export interface GenerateResult {
  success: boolean;
  outputPaths: string[];
  model: string;
  type: GenerationType;
  error?: string;
}
