import { NextRequest, NextResponse } from "next/server";

import { getBackendUrl } from "@/lib/api/backendUrl";

/**
 * API Route pour le chatbot
 *
 * Proxy vers le backend qui utilise OpenAI pour répondre aux questions
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, conversation_history } = body;

    if (!message || typeof message !== "string") {
      return NextResponse.json({ error: "Message requis" }, { status: 400 });
    }

    let backendBase: string;
    try {
      backendBase = getBackendUrl();
    } catch (e) {
      return NextResponse.json(
        {
          error: e instanceof Error ? e.message : "Configuration backend invalide en production",
        },
        { status: 500 }
      );
    }

    try {
      const response = await fetch(`${backendBase}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          conversation_history: conversation_history || [],
        }),
      });

      if (!response.ok) {
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
          response:
            "Désolé, le service d'assistance mathématique n'est pas disponible pour le moment. Veuillez réessayer plus tard ou consulter les exercices disponibles sur la plateforme !",
        });
      }

      // Pour les autres erreurs, logger uniquement en développement
      if (process.env.NODE_ENV === "development") {
        console.error("Chat API error:", err);
      }
      return NextResponse.json({
        response:
          "Une erreur est survenue lors de la communication avec l'assistant. Veuillez réessayer.",
      });
    }
  } catch (error) {
    // Erreur lors du parsing du body ou autre erreur initiale
    if (process.env.NODE_ENV === "development") {
      console.error("Chat API error:", error);
    }
    return NextResponse.json(
      { response: "Une erreur est survenue. Veuillez réessayer." },
      { status: 500 }
    );
  }
}
