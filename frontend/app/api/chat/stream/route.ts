import { NextRequest } from "next/server";

/**
 * API Route pour le chatbot avec streaming SSE
 *
 * Proxy vers le backend qui utilise OpenAI avec streaming pour répondre aux questions
 * Best practice : Streaming pour meilleure UX - réponse progressive
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, conversation_history } = body;

    if (!message || typeof message !== "string") {
      return new Response(JSON.stringify({ error: "Message requis" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const backendUrl =
      process.env.NEXT_PUBLIC_API_BASE_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8000";

    try {
      const backendResponse = await fetch(`${backendUrl}/api/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          conversation_history: conversation_history || [],
          stream: true,
        }),
      });

      if (!backendResponse.ok) {
        throw new Error(`Backend error: ${backendResponse.status}`);
      }

      // Retourner le stream SSE directement au client
      return new Response(backendResponse.body, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
          "X-Accel-Buffering": "no",
        },
      });
    } catch (error: unknown) {
      const err = error as Error;
      const errorMessage = err?.message ?? String(error);

      // Gérer les erreurs de connexion
      if (
        errorMessage.includes("ECONNREFUSED") ||
        errorMessage.includes("fetch failed") ||
        errorMessage.includes("NetworkError")
      ) {
        return new Response(
          `data: ${JSON.stringify({ type: "error", message: "Service non disponible" })}\n\n`,
          {
            headers: {
              "Content-Type": "text/event-stream",
              "Cache-Control": "no-cache",
              Connection: "keep-alive",
            },
          }
        );
      }

      console.error("Chat Stream API error:", error);
      return new Response(
        `data: ${JSON.stringify({ type: "error", message: "Erreur lors de la connexion" })}\n\n`,
        {
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
          },
        }
      );
    }
  } catch (error) {
    console.error("Chat Stream API error:", error);
    return new Response(
      `data: ${JSON.stringify({ type: "error", message: "Erreur lors du traitement" })}\n\n`,
      {
        status: 500,
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
        },
      }
    );
  }
}
