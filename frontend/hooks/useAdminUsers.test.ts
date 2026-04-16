import { createElement, type ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import { useAdminUsers } from "@/hooks/useAdminUsers";

const { mockGet, mockPatch, mockPost, mockDelete } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPatch: vi.fn(),
  mockPost: vi.fn(),
  mockDelete: vi.fn(),
}));

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    api: {
      ...actual.api,
      get: mockGet,
      patch: mockPatch,
      post: mockPost,
      delete: mockDelete,
    },
  };
});

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  });
  return function W({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

const listUser = {
  id: 1,
  username: "u",
  email: "u@x.com",
  full_name: null,
  role: "apprenant" as const,
  is_active: true,
  created_at: null,
};

describe("useAdminUsers", () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockPatch.mockReset();
    mockPost.mockReset();
    mockDelete.mockReset();
  });

  it("loads users with default pagination", async () => {
    mockGet.mockResolvedValueOnce({ items: [listUser], total: 1 });

    const { result } = renderHook(() => useAdminUsers(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/users?skip=0&limit=20");
    expect(result.current.users).toHaveLength(1);
    expect(result.current.total).toBe(1);
    expect(result.current.error).toBeNull();
  });

  it("builds query with search, role, is_active", async () => {
    mockGet.mockResolvedValueOnce({ items: [], total: 0 });

    renderHook(() => useAdminUsers({ search: "ab", role: "enseignant", is_active: true, skip: 5, limit: 10 }), {
      wrapper: wrapper(),
    });

    await waitFor(() => expect(mockGet).toHaveBeenCalled());
    expect(mockGet).toHaveBeenCalledWith(
      "/api/admin/users?search=ab&role=enseignant&is_active=true&skip=5&limit=10"
    );
  });

  it("exposes query error", async () => {
    mockGet.mockRejectedValueOnce(new ApiClientError("nope", 500));

    const { result } = renderHook(() => useAdminUsers(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.error).not.toBeNull());
    expect(result.current.users).toEqual([]);
  });

  it("updateUserActive calls patch and invalidates on success", async () => {
    mockGet.mockResolvedValue({ items: [], total: 0 });
    mockPatch.mockResolvedValueOnce({ id: 1, username: "u", is_active: false, role: "apprenant" });

    const { result } = renderHook(() => useAdminUsers(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.updateUserActive({ userId: 1, isActive: false });
    });

    expect(mockPatch).toHaveBeenCalledWith("/api/admin/users/1", { is_active: false });
  });

  it("updateUserRole sends role in body", async () => {
    mockGet.mockResolvedValue({ items: [], total: 0 });
    mockPatch.mockResolvedValueOnce({ id: 1, username: "u", is_active: true, role: "admin" });

    const { result } = renderHook(() => useAdminUsers(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.updateUserRole({ userId: 2, role: "admin" });
    });

    expect(mockPatch).toHaveBeenCalledWith("/api/admin/users/2", { role: "admin" });
  });

  it("sendResetPassword and resendVerification call post", async () => {
    mockGet.mockResolvedValue({ items: [], total: 0 });
    mockPost.mockResolvedValue({ message: "ok" });

    const { result } = renderHook(() => useAdminUsers(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.sendResetPassword(3);
    });
    expect(mockPost).toHaveBeenCalledWith("/api/admin/users/3/send-reset-password", {});

    await act(async () => {
      await result.current.resendVerification(4);
    });
    expect(mockPost).toHaveBeenCalledWith("/api/admin/users/4/resend-verification", {});
  });

  it("deleteUser calls delete endpoint", async () => {
    mockGet.mockResolvedValue({ items: [], total: 0 });
    mockDelete.mockResolvedValueOnce({ message: "deleted" });

    const { result } = renderHook(() => useAdminUsers(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.deleteUser(9);
    });

    expect(mockDelete).toHaveBeenCalledWith("/api/admin/users/9");
  });
});
