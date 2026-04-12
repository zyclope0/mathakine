import { describe, expect, it } from "vitest";

import {
  buildContentSecurityPolicy,
  generateCspNonce,
} from "@/lib/security/buildContentSecurityPolicy";

describe("buildContentSecurityPolicy", () => {
  it("production uses nonce-based script-src and omits unsafe-inline and unsafe-eval", () => {
    const csp = buildContentSecurityPolicy({
      isDevelopment: false,
      scriptNonce: "dGVzdG5vbmNldmFsdWU",
    });

    expect(csp).toMatch(/script-src 'self' 'nonce-dGVzdG5vbmNldmFsdWU'/);
    const scriptSrc = csp.match(/script-src[^;]+/)?.[0] ?? "";
    expect(scriptSrc).not.toContain("unsafe-inline");
    expect(scriptSrc).not.toContain("unsafe-eval");
    expect(csp).toContain("object-src 'none'");
    expect(csp).toContain("form-action 'self'");
    expect(csp).toContain("frame-src 'none'");
    expect(csp).toContain("upgrade-insecure-requests");
    expect(csp).not.toContain("localhost:10000");
    expect(csp).toContain("https://*.sentry.io");
    expect(csp).toContain("https://*.mathakine.fun");
    expect(csp).toContain("worker-src 'self' blob:");
    expect(csp).toContain("https://fonts.googleapis.com");
    expect(csp).toContain("style-src 'self' 'unsafe-inline'");
  });

  it("throws when production is requested without scriptNonce", () => {
    expect(() => buildContentSecurityPolicy({ isDevelopment: false })).toThrow(
      "scriptNonce is required when isDevelopment is false"
    );
  });

  it("development keeps unsafe-inline, unsafe-eval and local backend in connect-src", () => {
    const csp = buildContentSecurityPolicy({ isDevelopment: true });

    expect(csp).toContain("script-src 'self' 'unsafe-inline' 'unsafe-eval'");
    expect(csp).toContain("http://localhost:10000");
    expect(csp).toContain("http://127.0.0.1:10000");
    expect(csp).not.toContain("upgrade-insecure-requests");
  });
});

describe("generateCspNonce", () => {
  it("returns a non-empty base64-looking string", () => {
    const a = generateCspNonce();
    const b = generateCspNonce();
    expect(a.length).toBeGreaterThan(8);
    expect(b.length).toBeGreaterThan(8);
    expect(a).not.toBe(b);
    expect(/^[A-Za-z0-9+/]+=*$/u.test(a)).toBe(true);
  });
});
