import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { LOCALE_COOKIE_NAME, getLocaleFromDocumentCookie } from "@/lib/localeCookie";
import { getPersistedLocale, useLocaleStore } from "@/lib/stores/localeStore";

describe("localeStore", () => {
  beforeEach(() => {
    localStorage.clear();
    document.cookie = `${LOCALE_COOKIE_NAME}=; Path=/; Max-Age=0`;
    document.documentElement.lang = "fr";
    useLocaleStore.setState({ locale: "fr" });
  });

  afterEach(() => {
    localStorage.clear();
    document.cookie = `${LOCALE_COOKIE_NAME}=; Path=/; Max-Age=0`;
  });

  it("setLocale updates the canonical cookie and html[lang]", () => {
    useLocaleStore.getState().setLocale("en");
    expect(document.documentElement.lang).toBe("en");
    expect(getLocaleFromDocumentCookie()).toBe("en");
    expect(document.cookie).toContain(`${LOCALE_COOKIE_NAME}=en`);
  });

  it("getPersistedLocale prefers cookie over localStorage", () => {
    localStorage.setItem(
      "locale-preferences",
      JSON.stringify({ state: { locale: "fr" }, version: 0 })
    );
    document.cookie = `${LOCALE_COOKIE_NAME}=en; Path=/`;
    expect(getPersistedLocale()).toBe("en");
  });
});
