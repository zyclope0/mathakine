/**
 * Optional post-login path override (e.g. register flow forces /dashboard after auto-login).
 * Module-local mutable state — not a global React store (FFI-L20C).
 */
let postLoginRedirectOverride: string | null = null;

export function setPostLoginRedirectOverride(path: string | null): void {
  postLoginRedirectOverride = path;
}

export function clearPostLoginRedirectOverride(): void {
  postLoginRedirectOverride = null;
}

/** Returns current override and clears it (login success path when not onboarding). */
export function consumePostLoginRedirectOverride(): string | null {
  const value = postLoginRedirectOverride;
  postLoginRedirectOverride = null;
  return value;
}
