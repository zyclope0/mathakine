import {
  buildContentSecurityPolicy,
  generateCspNonce,
} from "@/lib/security/buildContentSecurityPolicy";

/**
 * Internal request header: per-request nonce for **server** code that calls
 * `headers().get(CSP_NONCE_REQUEST_HEADER)` (e.g. future inline widgets, rare
 * Server Components). Prefer **nested** async layouts so `RootLayout` stays
 * static. Next.js still derives the **script** nonce from the
 * `Content-Security-Policy` header on the forwarded request, not from this
 * header. React Query Devtools in dev rely on `style-src 'unsafe-inline'`
 * (unchanged in QF-07A/B).
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
