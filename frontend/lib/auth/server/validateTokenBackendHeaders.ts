/**
 * Headers for server-side POST /api/auth/validate-token → backend.
 * Lets production logs attribute traffic (route loader vs sync-cookie).
 * Header can be spoofed by arbitrary HTTP clients; treat as a hint only.
 */
export const VALIDATE_TOKEN_CALLER_HEADER = "X-Mathakine-Validate-Caller";

export type ValidateTokenServerCaller = "routeSession" | "syncCookie";

export function buildValidateTokenRequestHeaders(
  caller: ValidateTokenServerCaller
): Record<string, string> {
  return {
    "Content-Type": "application/json",
    [VALIDATE_TOKEN_CALLER_HEADER]: caller,
  };
}
