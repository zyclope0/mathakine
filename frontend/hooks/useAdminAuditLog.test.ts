import { createElement, type ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import { getAuditActionLabel, useAdminAuditLog } from "@/hooks/useAdminAuditLog";

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }));

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    api: {
      ...actual.api,
      get: mockGet,
    },
  };
});

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return function W({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

describe("getAuditActionLabel", () => {
  it("returns mapped label for known action", () => {
    expect(getAuditActionLabel("user_patch")).toBe("Modif. utilisateur");
  });

  it("returns raw action when unknown", () => {
    expect(getAuditActionLabel("custom_action")).toBe("custom_action");
  });
});

describe("useAdminAuditLog", () => {
  beforeEach(() => {
    mockGet.mockReset();
  });

  it("returns items and total on success", async () => {
    mockGet.mockResolvedValueOnce({
      items: [{ id: 1, admin_user_id: 2, admin_username: "a", action: "x", resource_type: null, resource_id: null, details: null, created_at: "t" }],
      total: 1,
    });

    const { result } = renderHook(() => useAdminAuditLog(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.items).toHaveLength(1);
    expect(result.current.total).toBe(1);
    expect(result.current.error).toBeNull();
    expect(mockGet).toHaveBeenCalledWith("/api/admin/audit-log");
  });

  it("builds query string when params provided", async () => {
    mockGet.mockResolvedValueOnce({ items: [], total: 0 });

    const { result } = renderHook(
      () => useAdminAuditLog({ skip: 10, limit: 5, action: "user_patch", resource_type: "User" }),
      { wrapper: wrapper() }
    );

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith(
      "/api/admin/audit-log?skip=10&limit=5&action=user_patch&resource_type=User"
    );
    expect(result.current.items).toEqual([]);
  });

  it("exposes error when api.get rejects", async () => {
    mockGet.mockRejectedValueOnce(new ApiClientError("fail", 500));

    const { result } = renderHook(() => useAdminAuditLog(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.error).not.toBeNull());
    expect(result.current.items).toEqual([]);
    expect(result.current.total).toBe(0);
  });
});
