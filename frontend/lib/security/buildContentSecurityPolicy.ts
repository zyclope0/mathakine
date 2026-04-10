/**
 * Pure builder for the global Content-Security-Policy header string.
 * Emitted from `proxy.ts` (Edge middleware) so production can use a per-request
 * script nonce; Next.js reads the nonce from the incoming CSP header (see
 * `getScriptNonceFromHeader` in Next).
 */

export type BuildContentSecurityPolicyOptions = {
  isDevelopment: boolean;
  /** Required in production (`isDevelopment === false`). */
  scriptNonce?: string | undefined;
};

export function generateCspNonce(): string {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i] ?? 0);
  }
  return btoa(binary);
}

export function buildContentSecurityPolicy(options: BuildContentSecurityPolicyOptions): string {
  const { isDevelopment, scriptNonce } = options;

  const scriptSrc = isDevelopment
    ? "script-src 'self' 'unsafe-inline' 'unsafe-eval'"
    : (() => {
        if (!scriptNonce) {
          throw new Error(
            "buildContentSecurityPolicy: scriptNonce is required when isDevelopment is false"
          );
        }
        return `script-src 'self' 'nonce-${scriptNonce}'`;
      })();

  const backendDevConnect = isDevelopment ? "http://localhost:10000 http://127.0.0.1:10000" : "";

  const connectSrc = [
    "connect-src 'self'",
    backendDevConnect,
    "https://*.sentry.io",
    "https://*.ingest.sentry.io",
    "https://*.render.com",
    "https://*.onrender.com",
    "https://*.mathakine.fun",
  ]
    .filter(Boolean)
    .join(" ");

  return [
    "default-src 'self'",
    scriptSrc,
    "worker-src 'self' blob:",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src 'self' data: blob: https:",
    "font-src 'self' data: https://fonts.gstatic.com",
    connectSrc,
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "object-src 'none'",
    "form-action 'self'",
    "frame-src 'none'",
    ...(!isDevelopment ? ["upgrade-insecure-requests"] : []),
  ].join("; ");
}
