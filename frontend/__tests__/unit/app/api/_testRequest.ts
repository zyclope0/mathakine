import { NextRequest } from "next/server";

/** Requête POST JSON minimale pour les handlers de routes API Next. */
export function createPostJsonRequest(
  pathname: string,
  body: unknown,
  extraHeaders?: Record<string, string>
): NextRequest {
  return new NextRequest(`http://localhost${pathname}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...extraHeaders,
    },
    body: JSON.stringify(body),
  });
}
