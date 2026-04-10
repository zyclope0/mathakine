import {
  buildContentSecurityPolicy,
  generateCspNonce,
} from "@/lib/security/buildContentSecurityPolicy";

/**
 * Internal request header: nonce forwarded by `proxy.ts` for each matched request.
 * **QF-07C:** `app/layout.tsx` reads this and sets `nonce` on `<html>` so
 * production `script-src` nonce CSP matches inline Next.js bootstrap scripts.
 * Next also derives script nonce from the `Content-Security-Policy` request header
 * during dynamic renders. React Query Devtools in dev rely on `style-src
 * 'unsafe-inline'` (unchanged).
 */
export const CSP_NONCE_REQUEST_HEADER = "x-nonce" as const;

/**
 * One random nonce per middleware invocation. In production it is reused as
 * `scriptNonce` in CSP. In development CSP keeps `unsafe-inline` for scripts,
 * but the same nonce is still forwarded for optional `styleNonce` / tooling.
 */
export function buildMiddlewareCspBundle(isDevelopment: boolean): {
  csp: string;
  requestNonce: string;
} {
  const requestNonce = generateCspNonce();
  const csp = buildContentSecurityPolicy({
    isDevelopment,
    scriptNonce: isDevelopment ? undefined : requestNonce,
  });
  return { csp, requestNonce };
}
