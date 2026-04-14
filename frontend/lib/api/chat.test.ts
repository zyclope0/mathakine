import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { streamChat } from "./chat";

const { consumeSseJsonEventsMock } = vi.hoisted(() => ({
  consumeSseJsonEventsMock: vi.fn(),
}));

vi.mock("@/lib/utils/ssePostStream", () => ({
  consumeSseJsonEvents: consumeSseJsonEventsMock,
}));

describe("streamChat", () => {
  const originalFetch = global.fetch;
  const originalNavigatorLanguage = global.navigator.language;

  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubEnv("NODE_ENV", "production");
    Object.defineProperty(global.navigator, "language", {
      configurable: true,
      value: "fr-CH",
    });
    global.fetch = vi.fn().mockResolvedValue(
      new Response("", {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      })
    ) as typeof fetch;
    consumeSseJsonEventsMock.mockImplementation(async (_response, onEvent) => {
      await onEvent({ type: "done" });
    });
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    global.fetch = originalFetch;
    Object.defineProperty(global.navigator, "language", {
      configurable: true,
      value: originalNavigatorLanguage,
    });
  });

  it("posts directly to the public same-origin stream route without auth preflight headers", async () => {
    const onChunk = vi.fn();
    const onFinish = vi.fn();
    const onError = vi.fn();

    await streamChat(
      {
        message: "Bonjour",
        conversation_history: [],
        stream: true,
      },
      { onChunk, onFinish, onError }
    );

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/chat/stream",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
          Accept: "text/event-stream",
          "Accept-Language": "fr-CH",
        }),
      })
    );
    const [, requestInit] = vi.mocked(global.fetch).mock.calls[0] ?? [];
    expect(requestInit).toBeDefined();
    expect((requestInit as RequestInit).headers).not.toHaveProperty("X-CSRF-Token");
    expect(onFinish).toHaveBeenCalledTimes(1);
    expect(onError).not.toHaveBeenCalled();
    expect(onChunk).toHaveBeenCalledWith({ type: "done" });
  });
});
