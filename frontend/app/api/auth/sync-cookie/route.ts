/**
 * Route pour synchroniser le token d'accès sur le domaine frontend (cross-domain).
 * En production, le backend pose le cookie sur son domaine ; les requêtes vers les
 * routes API Next.js (même origine frontend) n'envoient pas ce cookie.
 * Cette route reçoit le token et le pose en cookie sur le domaine frontend.
 */
import { NextRequest } from "next/server";

const ACCESS_TOKEN_MAX_AGE = 60 * 60 * 24 * 7; // 7 jours (aligné avec le backend)

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const accessToken = body?.access_token;
    const clear = body?.clear === true;

    const isProduction = process.env.NODE_ENV === "production";

    if (clear || !accessToken) {
      // Effacer le cookie (logout)
      const cookieHeader = [
        "access_token=",
        "Path=/",
        "Max-Age=0",
        "HttpOnly",
        "SameSite=Lax",
        ...(isProduction ? ["Secure"] : []),
      ].join("; ");
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json", "Set-Cookie": cookieHeader },
      });
    }

    if (typeof accessToken !== "string") {
      return new Response(JSON.stringify({ error: "access_token requis" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const cookieHeader = [
      `access_token=${accessToken}`,
      "Path=/",
      `Max-Age=${ACCESS_TOKEN_MAX_AGE}`,
      "HttpOnly",
      "SameSite=Lax",
      ...(isProduction ? ["Secure"] : []),
    ].join("; ");

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Set-Cookie": cookieHeader,
      },
    });
  } catch {
    return new Response(JSON.stringify({ error: "Requête invalide" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }
}
