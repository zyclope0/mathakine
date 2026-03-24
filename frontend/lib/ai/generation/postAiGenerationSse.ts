import { ensureFrontendAuthCookie, getCsrfTokenFromCookie } from "@/lib/api/client";

/** Routes Next.js (proxy → backend SSE). */
export const AI_GENERATION_SSE_PATH = {
  exercise: "/api/exercises/generate-ai-stream",
  challenge: "/api/challenges/generate-ai-stream",
} as const;

export type AiGenerationSsePath =
  (typeof AI_GENERATION_SSE_PATH)[keyof typeof AI_GENERATION_SSE_PATH];

export type AiGenerationRequestErrorCode =
  | "csrf_token_missing"
  | "http_401"
  | "http_403"
  | "http_backend";

/**
 * Erreur applicative stable pour la génération IA (CSRF / HTTP avant consommation SSE).
 * Les hooks mappent `code` vers des toasts i18n (pas d’exposition de détails techniques).
 */
export class AiGenerationRequestError extends Error {
  readonly code: AiGenerationRequestErrorCode;
  readonly httpStatus: number;

  constructor(code: AiGenerationRequestErrorCode, httpStatus = 0) {
    super(code);
    this.name = "AiGenerationRequestError";
    this.code = code;
    this.httpStatus = httpStatus;
  }
}

function parseJsonSafe(text: string): { error?: string; detail?: string; code?: string } | null {
  try {
    const v = JSON.parse(text) as { error?: string; detail?: string; code?: string };
    return v && typeof v === "object" ? v : null;
  } catch {
    return null;
  }
}

/**
 * POST JSON + en-têtes SSE — même socle pour exercices et défis.
 * - Vérifie le cookie CSRF lisible côté client avant l’envoi (évite un aller-retour silencieux sans en-tête).
 * - Sur réponse HTTP non OK : lève `AiGenerationRequestError` (le corps est consommé ; ne pas relire la Response).
 */
export async function postAiGenerationSse(
  path: AiGenerationSsePath,
  body: Record<string, unknown>,
  signal: AbortSignal
): Promise<Response> {
  await ensureFrontendAuthCookie();

  let csrfToken: string | null = null;
  if (typeof document !== "undefined") {
    csrfToken = getCsrfTokenFromCookie();
    if (!csrfToken?.trim()) {
      throw new AiGenerationRequestError("csrf_token_missing", 0);
    }
  }

  const response = await fetch(path, {
    method: "POST",
    credentials: "include",
    signal,
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...(csrfToken?.trim() ? { "X-CSRF-Token": csrfToken.trim() } : {}),
      "Accept-Language": typeof navigator !== "undefined" ? navigator.language : "fr",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let raw = "";
    try {
      raw = await response.text();
    } catch {
      raw = "";
    }
    const status = response.status;
    const parsed = parseJsonSafe(raw);

    if (status === 401) {
      throw new AiGenerationRequestError("http_401", 401);
    }
    if (status === 403 || parsed?.code === "EMAIL_VERIFICATION_REQUIRED") {
      throw new AiGenerationRequestError("http_403", 403);
    }
    throw new AiGenerationRequestError("http_backend", status);
  }

  return response;
}
