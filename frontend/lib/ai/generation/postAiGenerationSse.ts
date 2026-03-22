import { ensureFrontendAuthCookie, getCsrfTokenFromCookie } from "@/lib/api/client";

/** Routes Next.js (proxy → backend SSE). */
export const AI_GENERATION_SSE_PATH = {
  exercise: "/api/exercises/generate-ai-stream",
  challenge: "/api/challenges/generate-ai-stream",
} as const;

export type AiGenerationSsePath =
  (typeof AI_GENERATION_SSE_PATH)[keyof typeof AI_GENERATION_SSE_PATH];

/**
 * POST JSON + en-têtes SSE — même socle pour exercices et défis.
 * L’appelant vérifie `response.ok` et `content-type` avant `consumeSseJsonEvents`.
 */
export async function postAiGenerationSse(
  path: AiGenerationSsePath,
  body: Record<string, unknown>,
  signal: AbortSignal
): Promise<Response> {
  await ensureFrontendAuthCookie();
  const csrf = getCsrfTokenFromCookie();
  return fetch(path, {
    method: "POST",
    credentials: "include",
    signal,
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...(csrf ? { "X-CSRF-Token": csrf } : {}),
      "Accept-Language": typeof navigator !== "undefined" ? navigator.language : "fr",
    },
    body: JSON.stringify(body),
  });
}
