/**
 * Types partagés du chat discussionnel (home).
 * @see ./README.md
 */

export type ChatMessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatMessageRole;
  content: string;
  /** URL d'image retournée par le backend chat pour une requête illustrée. */
  imageUrl?: string;
  /** Erreur réseau / stream : contenu remplacé par le message utilisateur (i18n). */
  error?: boolean;
}

/**
 * Phase du transport (évite un empilement de booléens type isLoading/isStreaming).
 * - idle : prêt à envoyer
 * - pending : requête partie, aucun chunk texte encore
 * - streaming : réception des chunks
 */
export type ChatTransportPhase = "idle" | "pending" | "streaming";
