import { afterEach, describe, expect, it } from "vitest";

import {
  LOCALE_COOKIE_NAME,
  getLocaleFromDocumentCookie,
  parseAcceptLanguageHeader,
  parseLocaleCookieValue,
  resolveRequestLocale,
  resolveLocaleForHtml,
  setLocaleCookieClient,
} from "@/lib/localeCookie";

describe("localeCookie", () => {
  afterEach(() => {
    document.cookie = `${LOCALE_COOKIE_NAME}=; Path=/; Max-Age=0`;
  });

  it("parseLocaleCookieValue accepts fr and en only", () => {
    expect(parseLocaleCookieValue("fr")).toBe("fr");
    expect(parseLocaleCookieValue("en")).toBe("en");
    expect(parseLocaleCookieValue("de")).toBeNull();
    expect(parseLocaleCookieValue(undefined)).toBeNull();
  });

  it("resolveLocaleForHtml falls back to fr", () => {
    expect(resolveLocaleForHtml(undefined)).toBe("fr");
    expect(resolveLocaleForHtml("")).toBe("fr");
    expect(resolveLocaleForHtml("en")).toBe("en");
  });

  it("parseAcceptLanguageHeader resolves the highest-priority supported locale", () => {
    expect(parseAcceptLanguageHeader("en-US,en;q=0.9,fr;q=0.8")).toBe("en");
    expect(parseAcceptLanguageHeader("de-DE,de;q=0.9,fr;q=0.7")).toBe("fr");
    expect(parseAcceptLanguageHeader("es-ES,pt;q=0.8")).toBeNull();
  });

  it("resolveRequestLocale prefers cookie over Accept-Language", () => {
    expect(
      resolveRequestLocale({
        cookieLocale: "fr",
        acceptLanguage: "en-US,en;q=0.9",
      })
    ).toBe("fr");
    expect(
      resolveRequestLocale({
        cookieLocale: undefined,
        acceptLanguage: "en-US,en;q=0.9",
      })
    ).toBe("en");
  });

  it("setLocaleCookieClient and getLocaleFromDocumentCookie round-trip", () => {
    setLocaleCookieClient("en");
    expect(getLocaleFromDocumentCookie()).toBe("en");
    setLocaleCookieClient("fr");
    expect(getLocaleFromDocumentCookie()).toBe("fr");
  });
});
