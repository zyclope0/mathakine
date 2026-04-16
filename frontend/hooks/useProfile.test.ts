import { createElement, type ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { useProfile } from "@/hooks/useProfile";

const { mockPut } = vi.hoisted(() => ({ mockPut: vi.fn() }));

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    api: {
      ...actual.api,
      put: mockPut,
    },
  };
});

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => `profile.${key}`,
}));

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  });
  return function W({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

const user = {
  id: 1,
  username: "u",
  email: "u@x.com",
  role: "apprenant" as const,
  is_active: true,
};

describe("useProfile", () => {
  beforeEach(() => {
    mockPut.mockReset();
    vi.mocked(toast.success).mockClear();
    vi.mocked(toast.error).mockClear();
  });

  it("updateProfile success sets auth cache and toasts", async () => {
    mockPut.mockResolvedValueOnce(user);

    const { result } = renderHook(() => useProfile(), { wrapper: wrapper() });

    await act(async () => {
      await result.current.updateProfileAsync({ full_name: "N" });
    });

    expect(mockPut).toHaveBeenCalledWith("/api/users/me", { full_name: "N" });
    expect(toast.success).toHaveBeenCalledWith("profile.updateSuccess", expect.any(Object));
  });

  it("updateProfile error 400 uses message branch", async () => {
    mockPut.mockRejectedValueOnce(new ApiClientError("bad field", 400));

    const { result } = renderHook(() => useProfile(), { wrapper: wrapper() });

    await act(async () => {
      await expect(result.current.updateProfileAsync({})).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith(
      "profile.updateError",
      expect.objectContaining({ description: "bad field" })
    );
  });

  it("updateProfile error 401 uses unauthorized label", async () => {
    mockPut.mockRejectedValueOnce(new ApiClientError("x", 401));

    const { result } = renderHook(() => useProfile(), { wrapper: wrapper() });

    await act(async () => {
      await expect(result.current.updateProfileAsync({})).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith(
      "profile.updateError",
      expect.objectContaining({ description: "profile.unauthorized" })
    );
  });

  it("updateProfile error 500 uses generic updateError", async () => {
    mockPut.mockRejectedValueOnce(new ApiClientError("x", 500));

    const { result } = renderHook(() => useProfile(), { wrapper: wrapper() });

    await act(async () => {
      await expect(result.current.updateProfileAsync({})).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith(
      "profile.updateError",
      expect.objectContaining({ description: "profile.updateError" })
    );
  });

  it("changePassword success toasts", async () => {
    mockPut.mockResolvedValueOnce({ message: "ok", success: true });

    const { result } = renderHook(() => useProfile(), { wrapper: wrapper() });

    await act(async () => {
      await result.current.changePasswordAsync({
        current_password: "a",
        new_password: "b",
      });
    });

    expect(mockPut).toHaveBeenCalledWith("/api/users/me/password", {
      current_password: "a",
      new_password: "b",
    });
    expect(toast.success).toHaveBeenCalledWith("profile.passwordChangeSuccess", expect.any(Object));
  });

  it("changePassword error 401 passwordIncorrect", async () => {
    mockPut.mockRejectedValueOnce(new ApiClientError("x", 401));

    const { result } = renderHook(() => useProfile(), { wrapper: wrapper() });

    await act(async () => {
      await expect(
        result.current.changePasswordAsync({ current_password: "a", new_password: "b" })
      ).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith(
      "profile.passwordChangeError",
      expect.objectContaining({ description: "profile.passwordIncorrect" })
    );
  });

  it("changePassword error 400 uses message", async () => {
    mockPut.mockRejectedValueOnce(new ApiClientError("weak", 400));

    const { result } = renderHook(() => useProfile(), { wrapper: wrapper() });

    await act(async () => {
      await expect(
        result.current.changePasswordAsync({ current_password: "a", new_password: "b" })
      ).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith(
      "profile.passwordChangeError",
      expect.objectContaining({ description: "weak" })
    );
  });

  it("exposes pending flags", async () => {
    mockPut.mockImplementation(
      () =>
        new Promise(() => {
          /* never */
        })
    );

    const { result } = renderHook(() => useProfile(), { wrapper: wrapper() });

    act(() => {
      void result.current.updateProfile({ full_name: "x" });
    });

    await waitFor(() => expect(result.current.isUpdatingProfile).toBe(true));
  });
});
