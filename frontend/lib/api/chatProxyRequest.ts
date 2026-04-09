/**
 * Shared helpers for Next.js → backend chat proxy routes (CHAT-AUTH-01).
 * Keeps cookie + CSRF forwarding aligned with other authenticated API proxies.
 */

import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { buildProxyForwardHeaders } from "@/lib/api/proxyForwardHeaders";

export function hasChatProxyAccessToken(request: NextRequest): boolean {
  return Boolean(request.cookies.get("access_token")?.value?.length);
}

export function buildChatBackendForwardHeaders(request: NextRequest): Record<string, string> {
  return buildProxyForwardHeaders(request);
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
