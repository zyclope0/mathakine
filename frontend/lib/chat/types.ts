/**
 * Types partages du chat discussionnel (home).
 * @see ./README.md
 */

export type ChatMessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatMessageRole;
  content: string;
  /** Excluded from `conversation_history` when false (eg. synthetic welcome message). */
  includeInHistory?: boolean;
  /** URL d'image retournee par le backend chat pour une requete illustree. */
  imageUrl?: string;
  /** Erreur reseau / stream : contenu remplace par le message utilisateur (i18n). */
  error?: boolean;
}

/**
 * Phase du transport (evite un empilement de booleens type isLoading/isStreaming).
 * - idle : pret a envoyer
 * - pending : requete partie, aucun chunk texte encore
 * - streaming : reception des chunks
 */
export type ChatTransportPhase = "idle" | "pending" | "streaming";
