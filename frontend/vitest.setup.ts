import "@testing-library/jest-dom";
import { cleanup } from "@testing-library/react";
import * as React from "react";
import { afterEach, vi } from "vitest";

// Stabilize test runtime: avoid booting real confetti animation loops in jsdom.
vi.mock("canvas-confetti", () => ({
  default: vi.fn(),
}));

// Cleanup after each test (jsdom only; node env suites do not have `window`)
afterEach(() => {
  if (typeof window !== "undefined") {
    cleanup();
  }
});

// Mock Next.js router
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
    pathname: "/",
    query: {},
    asPath: "/",
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock Next.js Image
vi.mock("next/image", () => ({
  default: (props: React.ComponentProps<"img">) => React.createElement("img", props),
}));

// Mock window.matchMedia for media queries (jsdom only)
if (typeof window !== "undefined") {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });

  Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
    writable: true,
    value: vi.fn().mockReturnValue({
      clearRect: vi.fn(),
      fillRect: vi.fn(),
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      stroke: vi.fn(),
      fill: vi.fn(),
      save: vi.fn(),
      restore: vi.fn(),
      translate: vi.fn(),
      rotate: vi.fn(),
      scale: vi.fn(),
      setTransform: vi.fn(),
      arc: vi.fn(),
      closePath: vi.fn(),
      canvas: { width: 0, height: 0 },
    }),
  });
}

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock as unknown as Storage;
