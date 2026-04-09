/**
 * Shared helpers for Next.js → backend chat proxy routes (CHAT-AUTH-01).
 * Keeps cookie + CSRF forwarding aligned with other authenticated API proxies.
 */

import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export function hasChatProxyAccessToken(request: NextRequest): boolean {
  return Boolean(request.cookies.get("access_token")?.value?.length);
}

export function buildChatBackendForwardHeaders(request: NextRequest): Record<string, string> {
  const cookies = request.cookies
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ");
  return {
    "Content-Type": "application/json",
    Cookie: cookies,
    "X-CSRF-Token": request.headers.get("X-CSRF-Token") ?? "",
    "Accept-Language": request.headers.get("Accept-Language") ?? "",
  };
}

/** Same shape as backend `api_error_json` for 401 (middleware). */
export function chatProxyUnauthorizedResponse(): NextResponse {
  return NextResponse.json(
    {
      code: "UNAUTHORIZED",
      message: "Authentication required",
      error: "Authentication required",
    },
    { status: 401 }
  );
}
