/**
 * Lecture d'un flux text/event-stream renvoyé par fetch() (POST + SSE-like).
 * EventSource natif ne supporte pas POST ; ce helper parse les lignes `data: {...}`.
 */

export type SseJsonEvent = Record<string, unknown>;

/**
 * Consomme le corps d'une Response en tant qu'événements SSE JSON (`data: ...`).
 * @param onEvent appelé pour chaque événement JSON valide ; peut être async.
 */
export async function consumeSseJsonEvents(
  response: Response,
  onEvent: (data: SseJsonEvent) => void | Promise<void>,
  options?: { signal?: AbortSignal }
): Promise<void> {
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Réponse sans corps lisible");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      if (options?.signal?.aborted) {
        await reader.cancel().catch(() => undefined);
        throw new DOMException("Aborted", "AbortError");
      }

      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data: ")) continue;
        try {
          const data = JSON.parse(trimmed.slice(6)) as SseJsonEvent;
          await onEvent(data);
        } catch {
          /* ignore non-JSON fragments */
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
