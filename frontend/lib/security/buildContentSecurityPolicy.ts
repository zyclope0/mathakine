/**
 * Pure builder for the global Content-Security-Policy header string.
 * Used from `next.config.ts` so dev vs prod differences stay explicit and testable.
 */

export function buildContentSecurityPolicy(isDevelopment: boolean): string {
  const scriptSrc = isDevelopment
    ? "script-src 'self' 'unsafe-inline' 'unsafe-eval'"
    : "script-src 'self' 'unsafe-inline'";

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
