import { beforeEach, describe, expect, it, vi } from "vitest";

import { STORAGE_KEYS } from "../storage";
import { applyThemeDomState, readStoredDarkMode } from "./themeDom";

describe("themeDom", () => {
  beforeEach(() => {
    document.documentElement.className = "";
    document.documentElement.removeAttribute("data-theme");
    vi.restoreAllMocks();
  });

  it("lit dark-mode depuis le storage si présent", () => {
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: {
        getItem: vi.fn((key: string) => (key === STORAGE_KEYS.darkMode ? "true" : null)),
      },
    });

    expect(readStoredDarkMode()).toBe(true);
  });

  it("retombe sur prefers-color-scheme si aucune préférence stockée", () => {
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: {
        getItem: vi.fn(() => null),
      },
    });
    vi.stubGlobal(
      "matchMedia",
      vi.fn().mockReturnValue({
        matches: true,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })
    );

    expect(readStoredDarkMode()).toBe(true);
  });

  it("applique le thème et retire le verrou de transition après deux frames", () => {
    const callbacks: FrameRequestCallback[] = [];
    vi.stubGlobal(
      "requestAnimationFrame",
      vi.fn((cb: FrameRequestCallback) => callbacks.push(cb))
    );

    applyThemeDomState({ theme: "forest", isDark: true, disableTransitions: true });

    expect(document.documentElement.getAttribute("data-theme")).toBe("forest");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(document.documentElement.classList.contains("theme-switching")).toBe(true);

    callbacks.shift()?.(0);
    callbacks.shift()?.(0);

    expect(document.documentElement.classList.contains("theme-switching")).toBe(false);
  });
});
