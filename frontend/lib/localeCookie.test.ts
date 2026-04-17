import { afterEach, describe, expect, it } from "vitest";

import {
  LOCALE_COOKIE_NAME,
  getLocaleFromDocumentCookie,
  parseLocaleCookieValue,
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

  it("setLocaleCookieClient and getLocaleFromDocumentCookie round-trip", () => {
    setLocaleCookieClient("en");
    expect(getLocaleFromDocumentCookie()).toBe("en");
    setLocaleCookieClient("fr");
    expect(getLocaleFromDocumentCookie()).toBe("fr");
  });
});
