/**
 * Route pour synchroniser le token d'acces sur le domaine frontend (cross-domain).
 * En production, le backend pose le cookie sur son domaine ; les requetes vers les
 * routes API Next.js (meme origine frontend) n'envoient pas ce cookie.
 * Cette route recoit le token et le pose en cookie sur le domaine frontend.
 *
 * SECURITE: Le token est valide cote backend (signature + expiration) avant d'etre
 * pose en cookie, pour eviter le session hijacking via token forge.
 */
import { type NextRequest } from "next/server";

import { validateAccessTokenWithBackend } from "@/lib/auth/server/validateTokenRuntime";

const ACCESS_TOKEN_MAX_AGE = 15 * 60;
const JWT_SEGMENT_COUNT = 3;
const MAX_ACCESS_TOKEN_LENGTH = 2048;

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:10000" : "");

function getBackendUrl(): string {
  return BACKEND_URL || "http://localhost:10000";
}

function isSyntacticallyValidJwt(token: string): boolean {
  if (token.length === 0 || token.length > MAX_ACCESS_TOKEN_LENGTH) {
    return false;
  }

  const segments = token.split(".");
  return segments.length === JWT_SEGMENT_COUNT && segments.every((segment) => segment.length > 0);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const accessToken = body?.access_token;
    const clear = body?.clear === true;

    const isProduction = process.env.NODE_ENV === "production";

    if (clear || !accessToken) {
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

    if (!isSyntacticallyValidJwt(accessToken)) {
      return new Response(JSON.stringify({ error: "Format de token invalide" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const validation = await validateAccessTokenWithBackend(
      getBackendUrl(),
      accessToken,
      "syncCookie"
    );

    if (validation !== true) {
      return new Response(JSON.stringify({ error: "Token invalide ou expire" }), {
        status: 401,
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
    return new Response(JSON.stringify({ error: "Requete invalide" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }
}
