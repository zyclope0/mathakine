/**
 * Proxy SSE : POST JSON vers le backend (prompt et paramètres hors URL).
 */
import { type NextRequest } from "next/server";

import { proxySseGenerateAiStreamPost } from "@/lib/api/sseProxyRequest";

export async function POST(request: NextRequest) {
  return proxySseGenerateAiStreamPost(request, {
    backendPath: "/api/challenges/generate-ai-stream",
    debugContext: "Challenge AI Stream Proxy",
    unauthenticatedSseMessage: "Non authentifié - Cookie manquant",
    devRuntimeErrorLabel: "Erreur proxy SSE défis:",
  });
}
