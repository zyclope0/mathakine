import { createElement, type ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import type { User } from "@/types/api";
import { useSettings } from "@/hooks/useSettings";

const { mockGet, mockPut, mockDelete } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPut: vi.fn(),
  mockDelete: vi.fn(),
}));

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    api: {
      ...actual.api,
      get: mockGet,
      put: mockPut,
      delete: mockDelete,
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
  useTranslations: () => (key: string) => `settings.${key}`,
}));

vi.mock("@/lib/utils/debug", () => ({
  debugError: vi.fn(),
}));

function createWrapper(initialAuth?: User) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  });
  if (initialAuth) {
    client.setQueryData(["auth", "me"], initialAuth);
  }
  return function W({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

const baseUser: User = {
  id: 1,
  username: "u",
  email: "u@x.com",
  role: "apprenant",
  is_active: true,
};

describe("useSettings", () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockPut.mockReset();
    mockDelete.mockReset();
    vi.mocked(toast.success).mockClear();
    vi.mocked(toast.error).mockClear();
  });

  it("updateSettings success merges when auth cache exists", async () => {
    mockPut.mockResolvedValueOnce({ ...baseUser, language_preference: "en" });

    const { result } = renderHook(() => useSettings(), {
      wrapper: createWrapper(baseUser),
    });

    await act(async () => {
      await result.current.updateSettingsAsync({ language_preference: "en" });
    });

    expect(mockPut).toHaveBeenCalledWith("/api/users/me", { language_preference: "en" });
    expect(toast.success).toHaveBeenCalled();
  });

  it("updateSettings success when no prior auth cache uses updated user only", async () => {
    mockPut.mockResolvedValueOnce(baseUser);

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    await act(async () => {
      await result.current.updateSettingsAsync({ timezone: "UTC" });
    });

    expect(toast.success).toHaveBeenCalled();
  });

  it("updateSettings error 400 uses message", async () => {
    mockPut.mockRejectedValueOnce(new ApiClientError("invalid", 400));

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    await act(async () => {
      await expect(result.current.updateSettingsAsync({})).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith(
      "settings.updateError",
      expect.objectContaining({ description: "invalid" })
    );
  });

  it("updateSettings error 401 uses fixed copy", async () => {
    mockPut.mockRejectedValueOnce(new ApiClientError("x", 401));

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    await act(async () => {
      await expect(result.current.updateSettingsAsync({})).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith(
      "settings.updateError",
      expect.objectContaining({ description: "Non autorisé" })
    );
  });

  it("updateSettings error 500 uses generic", async () => {
    mockPut.mockRejectedValueOnce(new ApiClientError("x", 503));

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    await act(async () => {
      await expect(result.current.updateSettingsAsync({})).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith(
      "settings.updateError",
      expect.objectContaining({ description: "settings.updateError" })
    );
  });

  it("setOnUpdateSuccess runs callback after delay", async () => {
    vi.useFakeTimers();
    mockPut.mockResolvedValueOnce(baseUser);
    const onDone = vi.fn();

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });
    result.current.setOnUpdateSuccess(onDone);

    await act(async () => {
      await result.current.updateSettingsAsync({ timezone: "UTC" });
    });

    expect(onDone).not.toHaveBeenCalled();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(500);
    });
    expect(onDone).toHaveBeenCalledTimes(1);
    vi.useRealTimers();
  });

  it("exportData success triggers download and toast", async () => {
    const createObjectURL = vi.spyOn(window.URL, "createObjectURL").mockReturnValue("blob:u");
    const revokeObjectURL = vi.spyOn(window.URL, "revokeObjectURL").mockImplementation(() => {});
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    mockGet.mockResolvedValueOnce({ profile: true });

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    await act(async () => {
      await result.current.exportDataAsync();
    });

    expect(createObjectURL).toHaveBeenCalled();
    expect(clickSpy).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalled();

    createObjectURL.mockRestore();
    revokeObjectURL.mockRestore();
    clickSpy.mockRestore();
  });

  it("exportData error toasts", async () => {
    mockGet.mockRejectedValueOnce(new Error("network"));

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    await act(async () => {
      await expect(result.current.exportDataAsync()).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith("settings.exportError", expect.any(Object));
  });

  it("deleteAccount error toasts", async () => {
    mockDelete.mockRejectedValueOnce(new Error("no"));

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    await act(async () => {
      await expect(result.current.deleteAccountAsync()).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith("settings.deleteError", expect.any(Object));
  });

  it("getSessions returns empty array on error", async () => {
    mockGet.mockRejectedValueOnce(new Error("fail"));

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    let sessions: unknown;
    await act(async () => {
      sessions = await result.current.getSessions();
    });

    expect(sessions).toEqual([]);
  });

  it("getSessions returns data on success", async () => {
    mockGet.mockImplementationOnce((url: string) => {
      if (url.startsWith("/api/users/me/sessions")) {
        return Promise.resolve([
          { id: 1, last_activity: "t", created_at: "t", expires_at: "t", is_active: true },
        ]);
      }
      return Promise.reject(new Error(`unexpected ${url}`));
    });

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    let sessions: unknown;
    await act(async () => {
      sessions = await result.current.getSessions();
    });

    expect(Array.isArray(sessions)).toBe(true);
    expect((sessions as { id: number }[])[0]?.id).toBe(1);
  });

  it("revokeSession success invalidates and toasts", async () => {
    mockDelete.mockResolvedValueOnce({});

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    await act(async () => {
      await result.current.revokeSession(3);
    });

    expect(mockDelete).toHaveBeenCalledWith("/api/users/me/sessions/3");
    expect(toast.success).toHaveBeenCalled();
  });

  it("revokeSession error toasts", async () => {
    mockDelete.mockRejectedValueOnce(new Error("x"));

    const { result } = renderHook(() => useSettings(), { wrapper: createWrapper() });

    await act(async () => {
      result.current.revokeSession(1);
    });

    await waitFor(() =>
      expect(toast.error).toHaveBeenCalledWith(
        "Erreur",
        expect.objectContaining({ description: expect.any(String) })
      )
    );
  });
});
