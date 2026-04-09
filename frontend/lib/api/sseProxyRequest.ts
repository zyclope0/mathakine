/**
 * Shared Next.js → backend proxy for pedagogical SSE POST routes (exercises / challenges).
 * Keeps JSON parse/validate, cookie + CSRF + language forwarding, and stream wiring aligned.
 */

import type { NextRequest } from "next/server";

import { getBackendUrl } from "@/lib/api/backendUrl";
import { buildProxyForwardHeaders } from "@/lib/api/proxyForwardHeaders";
import { logInDevelopment } from "@/lib/utils/logInDevelopment";

const JSON_HEADERS: Record<string, string> = {
  "Content-Type": "application/json",
};

const SSE_RESPONSE_HEADERS: Record<string, string> = {
  "Content-Type": "text/event-stream",
  "Cache-Control": "no-cache",
  Connection: "keep-alive",
};

const SSE_OK_STREAM_HEADERS: Record<string, string> = {
  ...SSE_RESPONSE_HEADERS,
  "X-Accel-Buffering": "no",
};

const EMPTY_STREAM_SSE_MESSAGE = "Réponse vide du service IA. Réessayez dans quelques instants.";

export interface ProxySseGenerateAiStreamConfig {
  /** Path on the backend origin, e.g. `/api/exercises/generate-ai-stream` */
  backendPath: string;
  debugContext?: string;
  /** `message` field inside the SSE `data:` JSON when `access_token` is absent */
  unauthenticatedSseMessage: string;
  /** First argument to `console.error` in development when the outer try/catch fires */
  devRuntimeErrorLabel: string;
}

function joinBackendUrl(base: string, path: string): string {
  const trimmedBase = base.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${trimmedBase}${normalizedPath}`;
}

function sseErrorResponse(message: string): Response {
  return new Response(`data: ${JSON.stringify({ type: "error", message })}\n\n`, {
    status: 200,
    headers: SSE_RESPONSE_HEADERS,
  });
}

function logMissingAccessToken(request: NextRequest, debugContext?: string): void {
  logInDevelopment(() => {
    const cookieNames = request.cookies.getAll().map((cookie) => cookie.name);
    const contextPrefix = debugContext ? `[${debugContext}] ` : "";
    console.error(
      `${contextPrefix}Missing auth cookie. Cookies reçus: ${cookieNames.join(", ") || "(aucun)"}`
    );
  });
}

/**
 * POST JSON body → backend SSE stream. Same contract as legacy per-route handlers.
 */
export async function proxySseGenerateAiStreamPost(
  request: NextRequest,
  config: ProxySseGenerateAiStreamConfig
): Promise<Response> {
  try {
    let payload: unknown;
    try {
      payload = await request.json();
    } catch {
      return new Response(JSON.stringify({ error: "Corps JSON invalide" }), {
        status: 422,
        headers: JSON_HEADERS,
      });
    }

    if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
      return new Response(JSON.stringify({ error: "Le corps doit être un objet JSON" }), {
        status: 400,
        headers: JSON_HEADERS,
      });
    }

    if (!request.cookies.get("access_token")) {
      logMissingAccessToken(request, config.debugContext);
      return sseErrorResponse(config.unauthenticatedSseMessage);
    }

    const backendUrl = joinBackendUrl(getBackendUrl(), config.backendPath);

    const backendResponse = await fetch(backendUrl, {
      method: "POST",
      headers: buildProxyForwardHeaders(request),
      body: JSON.stringify(payload),
      redirect: "manual",
    });

    if (!backendResponse.ok) {
      return new Response(
        JSON.stringify({
          error: `Backend error: ${backendResponse.status} ${backendResponse.statusText}`,
        }),
        {
          status: backendResponse.status,
          headers: JSON_HEADERS,
        }
      );
    }

    if (!backendResponse.body) {
      return sseErrorResponse(EMPTY_STREAM_SSE_MESSAGE);
    }

    return new Response(backendResponse.body, {
      headers: SSE_OK_STREAM_HEADERS,
    });
  } catch (error) {
    logInDevelopment(() => {
      console.error(config.devRuntimeErrorLabel, error);
    });
    return new Response(
      JSON.stringify({
        error: "Erreur lors de la connexion au backend",
        details: error instanceof Error ? error.message : String(error),
      }),
      {
        status: 500,
        headers: JSON_HEADERS,
      }
    );
  }
}
