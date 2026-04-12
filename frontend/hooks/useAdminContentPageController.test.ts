import { describe, it, expect } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAdminContentPageController } from "@/hooks/useAdminContentPageController";

function mockSearchParams(entries: Record<string, string>) {
  return {
    get: (key: string) => entries[key] ?? null,
  };
}

describe("useAdminContentPageController", () => {
  it("parses default tab and null edit", () => {
    const { result } = renderHook(() => useAdminContentPageController(mockSearchParams({})));
    expect(result.current.defaultTab).toBe("exercises");
    expect(result.current.editId).toBeNull();
  });

  it("parses challenges tab and edit id", () => {
    const { result } = renderHook(() =>
      useAdminContentPageController(mockSearchParams({ tab: "challenges", edit: "7" }))
    );
    expect(result.current.defaultTab).toBe("challenges");
    expect(result.current.editId).toBe(7);
  });

  it("invalid tab falls back to exercises", () => {
    const { result } = renderHook(() =>
      useAdminContentPageController(mockSearchParams({ tab: "invalid" }))
    );
    expect(result.current.defaultTab).toBe("exercises");
  });

  it("invalid edit id -> null", () => {
    const { result } = renderHook(() =>
      useAdminContentPageController(mockSearchParams({ edit: "nope" }))
    );
    expect(result.current.editId).toBeNull();
  });
});
