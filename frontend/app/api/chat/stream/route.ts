import { NextRequest, NextResponse } from "next/server";

import { getBackendUrl } from "@/lib/api/backendUrl";
import { getChatProxyCopy, resolveChatProxyLocale } from "@/lib/api/chatProxyLocale";
import {
  buildChatBackendForwardHeaders,
  chatProxyUnauthorizedResponse,
  hasChatProxyAccessToken,
} from "@/lib/api/chatProxyRequest";
import { logInDevelopment } from "@/lib/utils/logInDevelopment";

function logChatStreamError(error: unknown): void {
  logInDevelopment(() => {
    console.error("Chat Stream API error:", error);
  });
}

function sseChatErrorResponse(message: string, status: number = 200): Response {
  return new Response(`data: ${JSON.stringify({ type: "error", message })}\n\n`, {
    status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}

/**
 * API Route pour le chatbot avec streaming SSE
 *
 * Proxy vers le backend qui utilise OpenAI avec streaming pour répondre aux questions
 * Best practice : Streaming pour meilleure UX - réponse progressive
 */
export async function POST(request: NextRequest) {
  const proxyCopy = getChatProxyCopy(
    resolveChatProxyLocale(request.headers.get("Accept-Language"))
  );

  try {
    const body = await request.json();
    const { message, conversation_history } = body;

    if (!message || typeof message !== "string") {
      return new Response(JSON.stringify({ error: proxyCopy.messageRequired }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!hasChatProxyAccessToken(request)) {
      return chatProxyUnauthorizedResponse();
    }

    let backendBase: string;
    try {
      backendBase = getBackendUrl();
    } catch (e) {
      return new Response(
        JSON.stringify({
          error: e instanceof Error ? e.message : proxyCopy.backendConfigInvalid,
        }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    try {
      const backendResponse = await fetch(`${backendBase}/api/chat/stream`, {
        method: "POST",
        headers: buildChatBackendForwardHeaders(request),
        body: JSON.stringify({
          message,
          conversation_history: conversation_history || [],
          stream: true,
        }),
      });

      if (!backendResponse.ok) {
        if (backendResponse.status === 401 || backendResponse.status === 403) {
          const text = await backendResponse.text();
          try {
            const data: unknown = JSON.parse(text);
            if (data !== null && typeof data === "object" && !Array.isArray(data)) {
              return NextResponse.json(data, { status: backendResponse.status });
            }
          } catch {
            /* fall through */
          }
          return backendResponse.status === 401
            ? chatProxyUnauthorizedResponse()
            : NextResponse.json(
                {
                  code: "FORBIDDEN",
                  message: "CSRF token missing or invalid",
                  error: "CSRF token missing or invalid",
                },
                { status: 403 }
              );
        }
        throw new Error(`Backend error: ${backendResponse.status}`);
      }

      if (!backendResponse.body) {
        logChatStreamError(new Error("Chat stream backend returned an empty body"));
        return sseChatErrorResponse(proxyCopy.sseConnectionError);
      }

      // Retourner le stream SSE directement au client
      return new Response(backendResponse.body, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
          "X-Accel-Buffering": "no",
        },
      });
    } catch (error: unknown) {
      const err = error as Error;
      const errorMessage = err?.message ?? String(error);

      // Gérer les erreurs de connexion
      if (
        errorMessage.includes("ECONNREFUSED") ||
        errorMessage.includes("fetch failed") ||
        errorMessage.includes("NetworkError")
      ) {
        return sseChatErrorResponse(proxyCopy.sseServiceUnavailable);
      }

      logChatStreamError(error);
      return sseChatErrorResponse(proxyCopy.sseConnectionError);
    }
  } catch (error) {
    logChatStreamError(error);
    return sseChatErrorResponse(proxyCopy.sseProcessingError, 500);
  }
}
