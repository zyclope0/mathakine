/**
 * Proxy SSE : POST JSON vers le backend (prompt et paramètres hors URL).
 */
import { NextRequest } from "next/server";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:10000" : "");

function getBackendUrl(): string {
  const url =
    BACKEND_URL || (process.env.NODE_ENV === "development" ? "http://localhost:10000" : "");

  if (process.env.NODE_ENV === "production") {
    if (!url || url.includes("localhost")) {
      throw new Error(
        "NEXT_PUBLIC_API_BASE_URL doit être défini en production et ne peut pas être localhost"
      );
    }
  }

  return url;
}

export async function POST(request: NextRequest) {
  try {
    let payload: unknown;
    try {
      payload = await request.json();
    } catch {
      return new Response(JSON.stringify({ error: "Corps JSON invalide" }), {
        status: 422,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
      return new Response(JSON.stringify({ error: "Le corps doit être un objet JSON" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const allCookies = request.cookies.getAll();
    const cookies = allCookies.map((cookie) => `${cookie.name}=${cookie.value}`).join("; ");

    const hasAuthCookie = request.cookies.get("access_token");
    const cookieNames = request.cookies.getAll().map((c) => c.name);

    if (!hasAuthCookie) {
      console.error(
        "[Exercise AI Stream Proxy] Missing auth cookie. Cookies reçus:",
        cookieNames.join(", ") || "(aucun)"
      );
      return new Response(
        `data: ${JSON.stringify({
          type: "error",
          message: "Non authentifié - Cookie manquant. Déconnectez-vous puis reconnectez-vous.",
        })}\n\n`,
        {
          status: 200,
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
          },
        }
      );
    }

    const backendUrl = `${getBackendUrl()}/api/exercises/generate-ai-stream`;

    const backendResponse = await fetch(backendUrl, {
      method: "POST",
      headers: {
        Cookie: cookies,
        "Content-Type": "application/json",
        "X-CSRF-Token": request.headers.get("X-CSRF-Token") ?? "",
        "Accept-Language": request.headers.get("Accept-Language") ?? "",
      },
      body: JSON.stringify(payload),
      redirect: "manual",
    });

    if (!backendResponse.ok && backendResponse.status !== 200) {
      return new Response(
        JSON.stringify({
          error: `Backend error: ${backendResponse.status} ${backendResponse.statusText}`,
        }),
        {
          status: backendResponse.status,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    return new Response(backendResponse.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (error) {
    if (process.env.NODE_ENV === "development") {
      console.error("Erreur proxy SSE exercices:", error);
    }
    return new Response(
      JSON.stringify({
        error: "Erreur lors de la connexion au backend",
        details: error instanceof Error ? error.message : String(error),
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
