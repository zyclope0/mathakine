/** @vitest-environment jsdom */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api/client", () => ({
  ensureFrontendAuthCookie: vi.fn().mockResolvedValue(undefined),
  getCsrfTokenFromCookie: vi.fn(),
}));

import * as client from "@/lib/api/client";
import { getAiGenerationRequestErrorToast } from "@/lib/ai/generation/getAiGenerationRequestErrorToast";
import {
  AiGenerationRequestError,
  AI_GENERATION_SSE_PATH,
  postAiGenerationSse,
} from "@/lib/ai/generation/postAiGenerationSse";

describe("postAiGenerationSse", () => {
  beforeEach(() => {
    vi.mocked(client.getCsrfTokenFromCookie).mockReturnValue("csrf-test");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        body: new ReadableStream({
          start(c) {
            c.close();
          },
        }),
      } as Response)
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("throws csrf_token_missing and skips fetch when CSRF cookie is absent", async () => {
    vi.mocked(client.getCsrfTokenFromCookie).mockReturnValue(null);
    await expect(
      postAiGenerationSse(AI_GENERATION_SSE_PATH.exercise, { a: 1 }, new AbortController().signal)
    ).rejects.toMatchObject({ code: "csrf_token_missing", name: "AiGenerationRequestError" });
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("throws csrf_token_missing when CSRF is whitespace only", async () => {
    vi.mocked(client.getCsrfTokenFromCookie).mockReturnValue("   ");
    await expect(
      postAiGenerationSse(AI_GENERATION_SSE_PATH.exercise, {}, new AbortController().signal)
    ).rejects.toMatchObject({ code: "csrf_token_missing" });
  });

  it("returns ok Response and forwards X-CSRF-Token header", async () => {
    const res = await postAiGenerationSse(
      AI_GENERATION_SSE_PATH.exercise,
      { exercise_type: "addition", age_group: "6-8" },
      new AbortController().signal
    );
    expect(res.ok).toBe(true);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      AI_GENERATION_SSE_PATH.exercise,
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-test",
          Accept: "text/event-stream",
        }),
      })
    );
  });

  it("throws http_401 when backend returns 401", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 401,
      text: async () => "{}",
    } as Response);
    await expect(
      postAiGenerationSse(AI_GENERATION_SSE_PATH.challenge, { x: 1 }, new AbortController().signal)
    ).rejects.toMatchObject({ code: "http_401", httpStatus: 401 });
  });

  it("throws http_403 when backend returns 403", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 403,
      text: async () => JSON.stringify({ error: "Forbidden" }),
    } as Response);
    await expect(
      postAiGenerationSse(AI_GENERATION_SSE_PATH.exercise, { x: 1 }, new AbortController().signal)
    ).rejects.toMatchObject({ code: "http_403", httpStatus: 403 });
  });

  it("throws http_backend on 500", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 500,
      text: async () => JSON.stringify({ error: "oops" }),
    } as Response);
    await expect(
      postAiGenerationSse(AI_GENERATION_SSE_PATH.exercise, { x: 1 }, new AbortController().signal)
    ).rejects.toMatchObject({ code: "http_backend", httpStatus: 500 });
  });

  it("maps EMAIL_VERIFICATION_REQUIRED in JSON body to http_403", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 400,
      text: async () => JSON.stringify({ code: "EMAIL_VERIFICATION_REQUIRED" }),
    } as Response);
    await expect(
      postAiGenerationSse(AI_GENERATION_SSE_PATH.challenge, { x: 1 }, new AbortController().signal)
    ).rejects.toMatchObject({ code: "http_403" });
  });
});

describe("getAiGenerationRequestErrorToast", () => {
  const t = (key: string) => key;

  it("maps error codes to stable i18n keys", () => {
    expect(
      getAiGenerationRequestErrorToast(new AiGenerationRequestError("csrf_token_missing"), t).title
    ).toBe("aiGenerator.errorCsrfTitle");
    expect(
      getAiGenerationRequestErrorToast(new AiGenerationRequestError("http_401", 401), t).title
    ).toBe("aiGenerator.errorSessionTitle");
    expect(
      getAiGenerationRequestErrorToast(new AiGenerationRequestError("http_403", 403), t).title
    ).toBe("aiGenerator.errorAccessTitle");
    expect(
      getAiGenerationRequestErrorToast(new AiGenerationRequestError("http_backend", 503), t).title
    ).toBe("aiGenerator.errorBackendTitle");
  });
});
