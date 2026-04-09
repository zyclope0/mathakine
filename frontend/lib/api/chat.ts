import { getCsrfTokenFromCookie } from "@/lib/api/client";
import { consumeSseJsonEvents, type SseJsonEvent } from "@/lib/utils/ssePostStream";

/** Route Next (proxy → backend), même origine + cookies. */
export const CHAT_STREAM_PATH = "/api/chat/stream";

export interface ChatStreamPayload {
  message: string;
  conversation_history: Array<{ role: "user" | "assistant"; content: string }>;
  stream: true;
}

export type ChatStreamChunk =
  | { type: "chunk"; content: string }
  | { type: "status"; message: string }
  | { type: "image"; url: string }
  | { type: "done" }
  | { type: "error"; message: string };

/**
 * Valide / normalise un événement SSE JSON vers {@link ChatStreamChunk}.
 * Exporté pour tests unitaires (non-régression parsing).
 */
export function parseChatStreamEvent(data: unknown): ChatStreamChunk | null {
  if (typeof data !== "object" || data === null || !("type" in data)) {
    return null;
  }
  const rec = data as Record<string, unknown>;
  const type = rec.type;
  if (type === "chunk" && typeof rec.content === "string") {
    return { type: "chunk", content: rec.content };
  }
  if (type === "status" && typeof rec.message === "string") {
    return { type: "status", message: rec.message };
  }
  if (type === "image" && typeof rec.url === "string") {
    return { type: "image", url: rec.url };
  }
  if (type === "done") {
    return { type: "done" };
  }
  if (type === "error" && typeof rec.message === "string") {
    return { type: "error", message: rec.message };
  }
  return null;
}

export interface StreamChatCallbacks {
  onChunk: (chunk: ChatStreamChunk) => void;
  onFinish: () => void;
  onError: (error: Error) => void;
}

export interface StreamChatOptions {
  signal?: AbortSignal;
}

/**
 * Streaming chat (POST + SSE). Ne passe pas par `api.post` (corps stream).
 */
export async function streamChat(
  payload: ChatStreamPayload,
  { onChunk, onFinish, onError }: StreamChatCallbacks,
  options?: StreamChatOptions
): Promise<void> {
  try {
    const csrf = getCsrfTokenFromCookie();
    const requestInit: RequestInit = {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
        "Accept-Language": typeof navigator !== "undefined" ? navigator.language : "fr",
        ...(csrf ? { "X-CSRF-Token": csrf } : {}),
      },
      body: JSON.stringify(payload),
    };
    if (options?.signal) {
      requestInit.signal = options.signal;
    }
    const response = await fetch(CHAT_STREAM_PATH, requestInit);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `API Error: ${response.status}`);
    }

    let finished = false;
    await consumeSseJsonEvents(
      response,
      async (data: SseJsonEvent) => {
        const chunk = parseChatStreamEvent(data);
        if (!chunk) return;
        onChunk(chunk);
        if (chunk.type === "done") {
          finished = true;
          onFinish();
        }
        if (chunk.type === "error") {
          throw new Error(chunk.message);
        }
      },
      options?.signal ? { signal: options.signal } : undefined
    );

    if (!finished) {
      onFinish();
    }
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      return;
    }
    onError(err instanceof Error ? err : new Error(String(err)));
  }
}
