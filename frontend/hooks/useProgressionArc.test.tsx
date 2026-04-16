import { describe, expect, it, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useProgressionArc } from "@/hooks/useProgressionArc";
import type { GamificationLevelIndicator } from "@/types/api";

const mockT = vi.fn((key: string, params?: Record<string, string>) => {
  if (params) {
    return `${key}:${JSON.stringify(params)}`;
  }
  return key;
});

vi.mock("next-intl", () => ({
  useTranslations: (namespace: string) => (key: string, params?: Record<string, string>) => {
    return mockT(`${namespace}.${key}`, params);
  },
}));

describe("useProgressionArc", () => {
  it("retourne null sans gamification_level", () => {
    const { result } = renderHook(() => useProgressionArc(undefined));
    expect(result.current.constellation).toBeNull();
  });

  it("construit constellation à partir de progression_rank", () => {
    const gl: GamificationLevelIndicator = {
      current: 3,
      current_xp: 1,
      next_level_xp: 100,
      progression_rank: "explorer",
    };
    const { result } = renderHook(() => useProgressionArc(gl));
    expect(result.current.constellation?.nodes).toHaveLength(4);
    expect(result.current.constellation?.nodes[2]?.state).toBe("current");
    expect(result.current.constellation?.ariaLabel).toContain(
      "homeLearner.progressionArc.ariaLabel"
    );
  });
});
