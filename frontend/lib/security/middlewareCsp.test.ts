import { afterEach, describe, expect, it, vi } from "vitest";

import * as cspBuilder from "@/lib/security/buildContentSecurityPolicy";
import { buildMiddlewareCspBundle } from "@/lib/security/middlewareCsp";

describe("buildMiddlewareCspBundle", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("production: requestNonce is the script nonce embedded in CSP", () => {
    vi.spyOn(cspBuilder, "generateCspNonce").mockReturnValue("fixedNonceValue");

    const { csp, requestNonce } = buildMiddlewareCspBundle(false);

    expect(requestNonce).toBe("fixedNonceValue");
    expect(csp).toContain("'nonce-fixedNonceValue'");
    const scriptSrc = csp.match(/script-src[^;]+/)?.[0] ?? "";
    expect(scriptSrc).not.toContain("unsafe-inline");
  });

  it("development: CSP keeps script unsafe-inline; requestNonce is still generated for x-nonce consumers", () => {
    vi.spyOn(cspBuilder, "generateCspNonce").mockReturnValue("devOnlyNonce");

    const { csp, requestNonce } = buildMiddlewareCspBundle(true);

    expect(requestNonce).toBe("devOnlyNonce");
    const scriptSrc = csp.match(/script-src[^;]+/)?.[0] ?? "";
    expect(scriptSrc).toContain("unsafe-inline");
    expect(scriptSrc).not.toContain("devOnlyNonce");
  });
});
