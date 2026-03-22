import type { ChatMessage } from "./types";

/**
 * Construit le tableau `conversation_history` pour l’API à partir des messages UI.
 * Exclut les messages assistant vides (placeholder stream / erreur non textuelle).
 */
export function toApiConversationHistory(
  messages: ChatMessage[],
  options?: { maxMessages?: number }
): Array<{ role: "user" | "assistant"; content: string }> {
  const max = options?.maxMessages ?? 5;
  return messages
    .filter((m) => m.role === "user" || (m.role === "assistant" && m.content.trim().length > 0))
    .slice(-max)
    .map((m) => ({ role: m.role, content: m.content }));
}
