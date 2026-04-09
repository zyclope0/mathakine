import type { NextRequest } from "next/server";

export function buildProxyForwardHeaders(request: NextRequest): Record<string, string> {
  const cookieHeader = request.cookies
    .getAll()
    .map((cookie) => `${cookie.name}=${cookie.value}`)
    .join("; ");

  return {
    Cookie: cookieHeader,
    "Content-Type": "application/json",
    "X-CSRF-Token": request.headers.get("X-CSRF-Token") ?? "",
    "Accept-Language": request.headers.get("Accept-Language") ?? "",
  };
}
