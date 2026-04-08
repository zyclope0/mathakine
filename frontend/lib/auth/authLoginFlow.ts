/**
 * Pure auth flow helpers for useAuth (FFI-L20C) — no React, no I/O.
 */
import { ApiClientError } from "@/lib/api/client";
import type { LoginErrorToastLabels } from "@/lib/auth/types";

/** True when /api/users/me should yield null user (session absent after refresh attempt). */
export function isAuthMeQueryUnauthenticatedError(err: unknown): boolean {
  return err instanceof ApiClientError && err.status === 401;
}

export function resolveLoginErrorDescription(
  error: ApiClientError,
  labels: LoginErrorToastLabels
): string {
  if (error.status === 403) {
    return error.message || labels.loginForbidden;
  }
  if (error.status === 401) {
    return labels.loginInvalidCredentials;
  }
  if (error.status === 400) {
    return error.message || labels.loginInvalidRequest;
  }
  if (error.status === 500) {
    return error.message || labels.loginServerError;
  }
  return error.message || labels.loginError;
}
