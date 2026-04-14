/** @vitest-environment node */

import { afterEach, describe, expect, it, vi } from "vitest";

import {
  resetValidateTokenRuntimeForTests,
  validateAccessTokenWithBackend,
  VALIDATE_TOKEN_SUCCESS_TTL_MS,
} from "./validateTokenRuntime";

const BASE = "http://localhost:10000";

describe("validateAccessTokenWithBackend", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    resetValidateTokenRuntimeForTests();
  });

  it("coalesces concurrent requests for the same token into one fetch", async () => {
    let resolveFetch!: (value: Response) => void;
    const fetchPromise = new Promise<Response>((resolve) => {
      resolveFetch = resolve;
    });

    const fetchMock = vi.fn().mockReturnValue(fetchPromise);
    vi.stubGlobal("fetch", fetchMock);

    const first = validateAccessTokenWithBackend(BASE, "same.token.here", "routeSession");
    const second = validateAccessTokenWithBackend(BASE, "same.token.here", "syncCookie");

    await Promise.resolve();
    expect(fetchMock).toHaveBeenCalledTimes(1);

    resolveFetch!(
      new Response(JSON.stringify({ valid: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );

    const [a, b] = await Promise.all([first, second]);
    expect(a).toBe(true);
    expect(b).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("does not promote 401 to valid on a follow-up call", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(null, { status: 401 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ valid: true }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      );
    vi.stubGlobal("fetch", fetchMock);

    const first = await validateAccessTokenWithBackend(BASE, "bad.token", "routeSession");
    const second = await validateAccessTokenWithBackend(BASE, "bad.token", "routeSession");

    expect(first).toBe(false);
    expect(second).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("reuses success within TTL without a second fetch", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-04-06T12:00:00.000Z"));

    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ valid: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    await validateAccessTokenWithBackend(BASE, "ok.token", "syncCookie");
    await validateAccessTokenWithBackend(BASE, "ok.token", "routeSession");

    expect(fetchMock).toHaveBeenCalledTimes(1);

    vi.advanceTimersByTime(VALIDATE_TOKEN_SUCCESS_TTL_MS + 1);
    await validateAccessTokenWithBackend(BASE, "ok.token", "routeSession");

    expect(fetchMock).toHaveBeenCalledTimes(2);
    vi.useRealTimers();
  });
});
