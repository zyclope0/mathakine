interface ChatStreamPayload {
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
 * Initiates a streaming chat request to the backend.
 *
 * This function does not use the standard `api.post` because it needs to handle
 * a streaming response (SSE), not a simple JSON response.
 *
 * @param payload The message and conversation history.
 * @param onChunk A callback function that will be called for each chunk of data received from the stream.
 * @param onFinish A callback function that will be called when the stream is finished.
 * @param onError A callback function that will be called if an error occurs.
 */
export async function streamChat(
  payload: ChatStreamPayload,
  {
    onChunk,
    onFinish,
    onError,
  }: {
    onChunk: (chunk: ChatStreamChunk) => void;
    onFinish: () => void;
    onError: (error: Error) => void;
  }
) {
  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    (process.env.NODE_ENV === "development" ? "http://localhost:10000" : "");

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      credentials: "include",
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `API Error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Could not read stream from response.");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6)) as ChatStreamChunk;
            onChunk(data);
            if (data.type === "done") {
              onFinish();
              return; // End the stream processing
            }
            if (data.type === "error") {
              throw new Error(data.message);
            }
          } catch (e) {
            console.error("Failed to parse SSE chunk:", e);
          }
        }
      }
    }

    onFinish();
  } catch (err) {
    onError(err as Error);
  }
}
