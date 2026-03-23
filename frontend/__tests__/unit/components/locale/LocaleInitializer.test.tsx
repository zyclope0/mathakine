import { act, render, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { LocaleInitializer } from "@/components/locale/LocaleInitializer";
import { useLocaleStore } from "@/lib/stores/localeStore";

describe("LocaleInitializer", () => {
  const originalNavigatorLanguage = navigator.language;

  beforeEach(() => {
    localStorage.clear();
    document.documentElement.lang = "fr";
    useLocaleStore.setState({ locale: "fr" });
  });

  afterEach(() => {
    Object.defineProperty(window.navigator, "language", {
      configurable: true,
      value: originalNavigatorLanguage,
    });
  });

  it("detecte la langue du navigateur a la premiere visite", async () => {
    Object.defineProperty(window.navigator, "language", {
      configurable: true,
      value: "en-US",
    });

    render(<LocaleInitializer />);

    await waitFor(() => {
      expect(useLocaleStore.getState().locale).toBe("en");
      expect(document.documentElement.lang).toBe("en");
    });
  });

  it("resynchronise html[lang] quand la locale du store change apres rehydratation", async () => {
    render(<LocaleInitializer />);

    act(() => {
      useLocaleStore.setState({ locale: "en" });
    });

    await waitFor(() => {
      expect(document.documentElement.lang).toBe("en");
    });
  });
});
