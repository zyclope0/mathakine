/**
 * Server-only runtime for POST /api/auth/validate-token (backend).
 *
 * FFI-L19B: deduplicate concurrent validations for the same token + base URL, and
 * reuse a very short-lived success result to avoid back-to-back duplicate round-trips
 * (e.g. sync-cookie then immediate RSC session work). No persistent storage.
 *
 * - In-flight coalescing: parallel callers share one fetch (same outcome).
 * - Success TTL: only HTTP 200 responses are cached; 401 and errors are never cached.
 * - Revocation: worst case a "valid" result may be reused for VALIDATE_TOKEN_SUCCESS_TTL_MS.
 *
 * Synchronous in-memory key `baseUrl + "\\0" + token` (no async gap before `inFlight` is set).
 * JWT payloads do not contain NUL; base URL is normalized — avoids `node:crypto` for Edge safety.
 */
import { buildValidateTokenRequestHeaders } from "@/lib/auth/server/validateTokenBackendHeaders";
import type { ValidateTokenServerCaller } from "@/lib/auth/server/validateTokenBackendHeaders";

/** Wall-clock reuse of a successful validation (milliseconds). Keep small (revocation visibility). */
export const VALIDATE_TOKEN_SUCCESS_TTL_MS = 2500;

const inFlightByKey = new Map<string, Promise<boolean | null>>();
const successExpiresAtByKey = new Map<string, number>();

function runtimeKey(baseUrl: string, token: string): string {
  return `${baseUrl}\0${token}`;
}

/**
 * Test hook: clears in-flight and success-only entries. Do not use in production code.
 */
export function resetValidateTokenRuntimeForTests(): void {
  inFlightByKey.clear();
  successExpiresAtByKey.clear();
}

/**
 * Ask the backend to validate the access token (signature/expiry server-side).
 * @returns true if 200 OK, false if 401, null if network/other HTTP failure.
 */
export async function validateAccessTokenWithBackend(
  baseUrl: string,
  token: string,
  caller: ValidateTokenServerCaller
): Promise<boolean | null> {
  const key = runtimeKey(baseUrl, token);
  const now = Date.now();
  const successUntil = successExpiresAtByKey.get(key);
  if (successUntil !== undefined) {
    if (successUntil > now) {
      return true;
    }
    successExpiresAtByKey.delete(key);
  }

  const existing = inFlightByKey.get(key);
  if (existing) {
    return existing;
  }

  let settle!: (value: boolean | null) => void;
  const pending = new Promise<boolean | null>((resolve) => {
    settle = resolve;
  });
  inFlightByKey.set(key, pending);

  void (async () => {
    let outcome: boolean | null = null;
    try {
      const response = await fetch(`${baseUrl}/api/auth/validate-token`, {
        method: "POST",
        headers: buildValidateTokenRequestHeaders(caller),
        body: JSON.stringify({ token }),
        cache: "no-store",
      });

      if (response.status === 401) {
        outcome = false;
      } else if (!response.ok) {
        outcome = null;
      } else {
        successExpiresAtByKey.set(key, Date.now() + VALIDATE_TOKEN_SUCCESS_TTL_MS);
        outcome = true;
      }
    } catch {
      outcome = null;
    } finally {
      inFlightByKey.delete(key);
      settle(outcome);
    }
  })();

  return pending;
}
