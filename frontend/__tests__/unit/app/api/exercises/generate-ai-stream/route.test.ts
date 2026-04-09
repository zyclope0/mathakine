/** @vitest-environment node */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "@/app/api/exercises/generate-ai-stream/route";
import * as backendUrl from "@/lib/api/backendUrl";

import { createPostJsonRequest } from "../../_testRequest";

describe("POST /api/exercises/generate-ai-stream", () => {
  beforeEach(() => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.spyOn(backendUrl, "getBackendUrl").mockReturnValue("https://api.test");
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("forwards JSON body, Cookie, X-CSRF-Token and Accept-Language to backend SSE", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      status: 200,
      body: new ReadableStream({
        start(c) {
          c.close();
        },
      }),
    } as Response);

    const payload = { exercise_type: "addition", age_group: "6-8", derived_difficulty: "INITIE" };
    const req = createPostJsonRequest("/api/exercises/generate-ai-stream", payload, {
      Cookie: "access_token=tok42; session=1",
      "X-CSRF-Token": "csrf-abc",
      "Accept-Language": "fr",
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("text/event-stream");

    expect(globalThis.fetch).toHaveBeenCalledWith(
      "https://api.test/api/exercises/generate-ai-stream",
      expect.objectContaining({
        method: "POST",
        headers: {
          Cookie: "access_token=tok42; session=1",
          "Content-Type": "application/json",
          "X-CSRF-Token": "csrf-abc",
          "Accept-Language": "fr",
        },
        body: JSON.stringify(payload),
        redirect: "manual",
      })
    );
  });

  it("returns JSON error with backend status when backend response is not ok", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 503,
      statusText: "Service Unavailable",
    } as Response);

    const req = createPostJsonRequest(
      "/api/exercises/generate-ai-stream",
      { exercise_type: "addition", age_group: "6-8" },
      { Cookie: "access_token=x" }
    );

    const res = await POST(req);
    expect(res.status).toBe(503);
    expect(res.headers.get("content-type")).toBe("application/json");
    const data = JSON.parse(await res.text());
    expect(data.error).toContain("503");
    expect(data.error).toContain("Service Unavailable");
  });

  it("returns SSE error when backend responds 200 with an empty stream body", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      status: 200,
      body: null,
    } as Response);

    const req = createPostJsonRequest(
      "/api/exercises/generate-ai-stream",
      { exercise_type: "addition", age_group: "6-8" },
      { Cookie: "access_token=x" }
    );

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("text/event-stream");
    const text = await res.text();
    expect(text).toContain("error");
    expect(text).toContain("Réponse vide");
  });

  it("returns SSE error when access_token cookie is missing (no backend call)", async () => {
    const req = createPostJsonRequest("/api/exercises/generate-ai-stream", {
      exercise_type: "addition",
      age_group: "6-8",
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("text/event-stream");
    const text = await res.text();
    expect(text).toContain("error");
    expect(text).toContain("Non authentifié");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("does not log missing auth cookie noise in production", async () => {
    vi.stubEnv("NODE_ENV", "production");

    const req = createPostJsonRequest("/api/exercises/generate-ai-stream", {
      exercise_type: "addition",
      age_group: "6-8",
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(console.error).not.toHaveBeenCalled();
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("returns 500 JSON when getBackendUrl throws after auth cookie present", async () => {
    vi.spyOn(backendUrl, "getBackendUrl").mockImplementation(() => {
      throw new Error("NEXT_PUBLIC_API_BASE_URL manquant");
    });

    const req = createPostJsonRequest(
      "/api/exercises/generate-ai-stream",
      { exercise_type: "addition", age_group: "6-8" },
      { Cookie: "access_token=y" }
    );

    const res = await POST(req);
    expect(res.status).toBe(500);
    const data = JSON.parse(await res.text());
    expect(data.error).toBe("Erreur lors de la connexion au backend");
    expect(data.details).toContain("NEXT_PUBLIC_API_BASE_URL");
  });
});
