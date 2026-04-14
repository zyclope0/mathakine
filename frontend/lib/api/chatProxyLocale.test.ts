import { describe, expect, it } from "vitest";

import { getChatProxyCopy, resolveChatProxyLocale } from "./chatProxyLocale";

describe("chatProxyLocale", () => {
  it("resolveChatProxyLocale defaults to fr", () => {
    expect(resolveChatProxyLocale(null)).toBe("fr");
    expect(resolveChatProxyLocale("")).toBe("fr");
    expect(resolveChatProxyLocale("fr-FR,fr;q=0.9")).toBe("fr");
  });

  it("resolveChatProxyLocale picks en when primary language is English", () => {
    expect(resolveChatProxyLocale("en")).toBe("en");
    expect(resolveChatProxyLocale("en-US")).toBe("en");
    expect(resolveChatProxyLocale("en-GB,en;q=0.9")).toBe("en");
  });

  it("getChatProxyCopy returns aligned fr/en strings", () => {
    const fr = getChatProxyCopy("fr");
    const en = getChatProxyCopy("en");
    expect(fr.messageRequired).toBe("Message requis");
    expect(en.messageRequired).toBe("Message is required");
    expect(fr.sseServiceUnavailable).toBe("Service non disponible");
    expect(en.sseServiceUnavailable).toBe("Service unavailable");
  });
});
