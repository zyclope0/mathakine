import { NextRequest, NextResponse } from "next/server";

import { getBackendUrl } from "@/lib/api/backendUrl";
import { getChatProxyCopy, resolveChatProxyLocale } from "@/lib/api/chatProxyLocale";
import {
  buildChatBackendForwardHeaders,
  chatProxyUnauthorizedResponse,
  hasChatProxyAccessToken,
} from "@/lib/api/chatProxyRequest";

/**
 * API Route pour le chatbot
 *
 * Proxy vers le backend qui utilise OpenAI pour répondre aux questions
 */
export async function POST(request: NextRequest) {
  const proxyCopy = getChatProxyCopy(
    resolveChatProxyLocale(request.headers.get("Accept-Language"))
  );

  try {
    const body = await request.json();
    const { message, conversation_history } = body;

    if (!message || typeof message !== "string") {
      return NextResponse.json({ error: proxyCopy.messageRequired }, { status: 400 });
    }

    if (!hasChatProxyAccessToken(request)) {
      return chatProxyUnauthorizedResponse();
    }

    let backendBase: string;
    try {
      backendBase = getBackendUrl();
    } catch (e) {
      return NextResponse.json(
        {
          error: e instanceof Error ? e.message : proxyCopy.backendConfigInvalid,
        },
        { status: 500 }
      );
    }

    try {
      const response = await fetch(`${backendBase}/api/chat`, {
        method: "POST",
        headers: buildChatBackendForwardHeaders(request),
        body: JSON.stringify({
          message,
          conversation_history: conversation_history || [],
        }),
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          const data = (await response.json().catch(() => null)) as Record<string, unknown> | null;
          if (data && typeof data === "object") {
            return NextResponse.json(data, { status: response.status });
          }
          return response.status === 401
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
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      return NextResponse.json(data);
    } catch (error: unknown) {
      // Si le backend n'est pas disponible, retourner une réponse de fallback
      const err = error as Error & { code?: string; cause?: { code?: string } };
      const errorMessage = err?.message ?? String(error);
      const errorCode = err?.code;
      const causeCode = err?.cause?.code;

      // Vérifier plusieurs façons dont l'erreur peut être signalée
      if (
        errorCode === "ECONNREFUSED" ||
        causeCode === "ECONNREFUSED" ||
        errorMessage.includes("ECONNREFUSED") ||
        errorMessage.includes("fetch failed") ||
        errorMessage.includes("NetworkError") ||
        (err?.cause && String(err.cause).includes("ECONNREFUSED"))
      ) {
        return NextResponse.json({
          response: proxyCopy.fallbackServiceUnavailable,
        });
      }

      // Pour les autres erreurs, logger uniquement en développement
      if (process.env.NODE_ENV === "development") {
        console.error("Chat API error:", err);
      }
      return NextResponse.json({
        response: proxyCopy.fallbackAssistantError,
      });
    }
  } catch (error) {
    // Erreur lors du parsing du body ou autre erreur initiale
    if (process.env.NODE_ENV === "development") {
      console.error("Chat API error:", error);
    }
    return NextResponse.json({ response: proxyCopy.fallbackGeneric }, { status: 500 });
  }
}
