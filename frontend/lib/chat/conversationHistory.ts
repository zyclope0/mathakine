import type { ChatMessage } from "./types";

/**
 * Construit le tableau `conversation_history` pour l'API a partir des messages UI.
 * Exclut les messages assistant vides (placeholder stream / erreur non textuelle)
 * et les messages synthétiques explicitement exclus de l'historique.
 */
export function toApiConversationHistory(
  messages: ChatMessage[],
  options?: { maxMessages?: number }
): Array<{ role: "user" | "assistant"; content: string }> {
  const max = options?.maxMessages ?? 5;
  return messages
    .filter(
      (message) =>
        message.includeInHistory !== false &&
        (message.role === "user" ||
          (message.role === "assistant" && message.content.trim().length > 0))
    )
    .slice(-max)
    .map((message) => ({ role: message.role, content: message.content }));
}
