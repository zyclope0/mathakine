import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import * as accessibilityStore from "@/lib/stores/accessibilityStore";
import * as reducedMotionHook from "@/lib/hooks/useSystemReducedMotion";

vi.mock("@/lib/hooks/useSystemReducedMotion", () => ({
  useSystemReducedMotion: vi.fn(() => false),
}));

// Mock store
vi.mock("@/lib/stores/accessibilityStore", () => ({
  useAccessibilityStore: vi.fn(),
}));

interface MockStoreValue {
  reducedMotion: boolean;
  focusMode: boolean;
  highContrast: boolean;
  largeText: boolean;
  dyslexiaMode: boolean;
  toggleHighContrast: () => void;
  toggleLargeText: () => void;
  toggleReducedMotion: () => void;
  toggleDyslexiaMode: () => void;
  toggleFocusMode: () => void;
  resetAll: () => void;
}

describe("useAccessibleAnimation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const getMockStoreValue = (overrides: Partial<MockStoreValue> = {}): MockStoreValue => ({
    reducedMotion: false,
    focusMode: false,
    highContrast: false,
    largeText: false,
    dyslexiaMode: false,
    toggleHighContrast: vi.fn(),
    toggleLargeText: vi.fn(),
    toggleReducedMotion: vi.fn(),
    toggleDyslexiaMode: vi.fn(),
    toggleFocusMode: vi.fn(),
    resetAll: vi.fn(),
    ...overrides,
  });

  it("retourne shouldReduceMotion false par défaut", () => {
    vi.mocked(accessibilityStore.useAccessibilityStore).mockReturnValue(getMockStoreValue());
    vi.mocked(reducedMotionHook.useSystemReducedMotion).mockReturnValue(false);

    const { result } = renderHook(() => useAccessibleAnimation());
    expect(result.current.shouldReduceMotion).toBe(false);
  });

  it("retourne shouldReduceMotion true si reducedMotion activé", () => {
    vi.mocked(accessibilityStore.useAccessibilityStore).mockReturnValue(
      getMockStoreValue({ reducedMotion: true })
    );
    vi.mocked(reducedMotionHook.useSystemReducedMotion).mockReturnValue(false);

    const { result } = renderHook(() => useAccessibleAnimation());
    expect(result.current.shouldReduceMotion).toBe(true);
  });

  it("retourne shouldReduceMotion true si focusMode activé", () => {
    vi.mocked(accessibilityStore.useAccessibilityStore).mockReturnValue(
      getMockStoreValue({ focusMode: true })
    );
    vi.mocked(reducedMotionHook.useSystemReducedMotion).mockReturnValue(false);

    const { result } = renderHook(() => useAccessibleAnimation());
    expect(result.current.shouldReduceMotion).toBe(true);
  });

  it("retourne shouldReduceMotion true si prefers-reduced-motion activé", () => {
    vi.mocked(accessibilityStore.useAccessibilityStore).mockReturnValue(getMockStoreValue());
    vi.mocked(reducedMotionHook.useSystemReducedMotion).mockReturnValue(true);

    const { result } = renderHook(() => useAccessibleAnimation());
    expect(result.current.shouldReduceMotion).toBe(true);
  });

  it("ignore focusMode si respectFocusMode vaut false", () => {
    vi.mocked(accessibilityStore.useAccessibilityStore).mockReturnValue(
      getMockStoreValue({ focusMode: true })
    );
    vi.mocked(reducedMotionHook.useSystemReducedMotion).mockReturnValue(false);

    const { result } = renderHook(() => useAccessibleAnimation({ respectFocusMode: false }));
    expect(result.current.shouldReduceMotion).toBe(false);
  });

  it("crée des variantes simplifiées si shouldReduceMotion est true", () => {
    vi.mocked(accessibilityStore.useAccessibilityStore).mockReturnValue(
      getMockStoreValue({ reducedMotion: true })
    );
    vi.mocked(reducedMotionHook.useSystemReducedMotion).mockReturnValue(false);

    const { result } = renderHook(() => useAccessibleAnimation());
    const variants = result.current.createVariants({
      initial: { opacity: 0, y: 20 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: -20 },
    });

    expect(variants.initial).toEqual({ opacity: 0 });
    expect(variants.animate).toEqual({ opacity: 1 });
    expect(variants.exit).toEqual({ opacity: 0 });
  });

  it("crée des transitions avec durée réduite si shouldReduceMotion est true", () => {
    vi.mocked(accessibilityStore.useAccessibilityStore).mockReturnValue(
      getMockStoreValue({ reducedMotion: true })
    );
    vi.mocked(reducedMotionHook.useSystemReducedMotion).mockReturnValue(false);

    const { result } = renderHook(() => useAccessibleAnimation());
    const transition = result.current.createTransition({ duration: 0.3, delay: 0.1 });

    expect(transition.duration).toBe(0.1);
    expect(transition.delay).toBe(0);
  });
});
