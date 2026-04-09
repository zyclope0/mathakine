/**
 * Proxy SSE : POST JSON vers le backend (prompt et paramètres hors URL).
 */
import { NextRequest } from "next/server";

import { proxySseGenerateAiStreamPost } from "@/lib/api/sseProxyRequest";

export async function POST(request: NextRequest) {
  return proxySseGenerateAiStreamPost(request, {
    backendPath: "/api/exercises/generate-ai-stream",
    debugContext: "Exercise AI Stream Proxy",
    unauthenticatedSseMessage:
      "Non authentifié - Cookie manquant. Déconnectez-vous puis reconnectez-vous.",
    devRuntimeErrorLabel: "Erreur proxy SSE exercices:",
  });
}
