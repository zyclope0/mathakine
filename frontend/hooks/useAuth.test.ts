import { createElement, type ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
}));

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    api: {
      get: mockGet,
      post: mockPost,
    },
  };
});

import { ApiClientError } from "@/lib/api/client";
import {
  clearFrontendAuthSyncCookie,
  syncAccessTokenToFrontend,
  syncCsrfTokenToFrontend,
} from "@/lib/auth/auth-session-sync";
import { clearPostLoginRedirectOverride } from "@/lib/auth/postLoginRedirect";
import { useAuth } from "@/hooks/useAuth";

const mockReplace = vi.fn();
const mockPush = vi.fn();
const mockRefresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    replace: mockReplace,
    push: mockPush,
    refresh: mockRefresh,
  }),
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock("@sentry/nextjs", () => ({
  setUser: vi.fn(),
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => key,
}));

vi.mock("@/lib/auth/auth-session-sync", () => ({
  syncAccessTokenToFrontend: vi.fn().mockResolvedValue(undefined),
  syncCsrfTokenToFrontend: vi.fn(),
  clearFrontendAuthSyncCookie: vi.fn().mockResolvedValue(undefined),
}));

import * as Sentry from "@sentry/nextjs";
import { toast } from "sonner";

function queryWrapper() {
  const client = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

describe("useAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    clearPostLoginRedirectOverride();
    mockGet.mockRejectedValue(new ApiClientError("unauthorized", 401));
    mockPost.mockReset();
  });

  afterEach(() => {
    clearPostLoginRedirectOverride();
  });

  it("login success syncs tokens, sets Sentry user, toasts, and redirects learner", async () => {
    mockPost.mockResolvedValueOnce({
      access_token: "access",
      token_type: "bearer",
      expires_in: 3600,
      csrf_token: "csrf",
      user: {
        id: 1,
        username: "learner",
        email: "l@x.com",
        role: "apprenant",
        is_active: true,
        onboarding_completed_at: "2020-01-01",
      },
    });

    const { result } = renderHook(() => useAuth(), { wrapper: queryWrapper() });

    await act(async () => {
      await result.current.loginAsync({ username: "learner", password: "secret" });
    });

    expect(syncAccessTokenToFrontend).toHaveBeenCalledWith("access");
    expect(syncCsrfTokenToFrontend).toHaveBeenCalledWith("csrf");
    expect(Sentry.setUser).toHaveBeenCalledWith({
      id: "1",
    });
    expect(toast.success).toHaveBeenCalled();
    expect(mockReplace).toHaveBeenCalledWith("/home-learner");
  });

  it("login success redirects to onboarding when onboarding not completed", async () => {
    mockPost.mockResolvedValueOnce({
      access_token: "access",
      token_type: "bearer",
      expires_in: 3600,
      user: {
        id: 2,
        username: "new",
        email: "n@x.com",
        role: "apprenant",
        is_active: true,
        onboarding_completed_at: null,
      },
    });

    const { result } = renderHook(() => useAuth(), { wrapper: queryWrapper() });

    await act(async () => {
      await result.current.loginAsync({ username: "new", password: "secret" });
    });

    expect(mockReplace).toHaveBeenCalledWith("/onboarding");
  });

  it("login error shows error toast with invalid-credentials copy on 401", async () => {
    mockPost.mockRejectedValueOnce(new ApiClientError("bad", 401));

    const { result } = renderHook(() => useAuth(), { wrapper: queryWrapper() });

    await act(async () => {
      try {
        await result.current.loginAsync({ username: "u", password: "p" });
      } catch {
        /* mutateAsync rethrows */
      }
    });

    expect(toast.error).toHaveBeenCalledWith(
      "loginError",
      expect.objectContaining({
        description: "loginInvalidCredentials",
      })
    );
  });

  it("logout clears Sentry user, toasts, clears cache, replaces home, refreshes", async () => {
    mockPost.mockResolvedValueOnce(undefined);

    const removeItem = vi.spyOn(Storage.prototype, "removeItem").mockImplementation(() => {});

    const { result } = renderHook(() => useAuth(), { wrapper: queryWrapper() });

    await act(async () => {
      result.current.logout();
    });

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith("/");
    });

    expect(Sentry.setUser).toHaveBeenCalledWith(null);
    expect(toast.success).toHaveBeenCalledWith("logoutSuccess");
    expect(mockReplace).toHaveBeenCalledWith("/");
    expect(mockRefresh).toHaveBeenCalled();
    expect(clearFrontendAuthSyncCookie).toHaveBeenCalled();

    removeItem.mockRestore();
  });

  it("forgot password success shows success toast", async () => {
    mockPost.mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useAuth(), { wrapper: queryWrapper() });

    await act(async () => {
      await result.current.forgotPasswordAsync({ email: "a@b.com" });
    });

    expect(toast.success).toHaveBeenCalledWith(
      "forgotPasswordSuccess",
      expect.objectContaining({ description: "forgotPasswordSuccessDescription" })
    );
  });

  it("register triggers auto-login and uses dashboard override when login succeeds", async () => {
    mockPost
      .mockResolvedValueOnce({
        id: 9,
        username: "reg",
        email: "r@x.com",
        role: "apprenant",
        is_active: true,
        onboarding_completed_at: "2020-01-01",
      })
      .mockResolvedValueOnce({
        access_token: "a",
        token_type: "bearer",
        expires_in: 3600,
        user: {
          id: 9,
          username: "reg",
          email: "r@x.com",
          role: "apprenant",
          is_active: true,
          onboarding_completed_at: "2020-01-01",
        },
      });

    const { result } = renderHook(() => useAuth(), { wrapper: queryWrapper() });

    await act(async () => {
      await result.current.registerAsync({
        username: "reg",
        email: "r@x.com",
        password: "pw",
      });
    });

    expect(mockPost).toHaveBeenCalled();
    expect(mockReplace).toHaveBeenCalledWith("/dashboard");
  });

  it("register falls back to login with verify when auto-login fails", async () => {
    mockPost
      .mockResolvedValueOnce({
        id: 10,
        username: "reg2",
        email: "r2@x.com",
        role: "apprenant",
        is_active: true,
        onboarding_completed_at: "2020-01-01",
      })
      .mockRejectedValueOnce(new ApiClientError("login failed", 401));

    const { result } = renderHook(() => useAuth(), { wrapper: queryWrapper() });

    await act(async () => {
      try {
        await result.current.registerAsync({
          username: "reg2",
          email: "r2@x.com",
          password: "pw",
        });
      } catch {
        /* swallowed in register onSuccess catch */
      }
    });

    expect(toast.success).toHaveBeenCalledWith(
      "registerSuccess",
      expect.objectContaining({ description: "registerVerifyEmailDescription" })
    );
    expect(mockPush).toHaveBeenCalledWith("/login?registered=true&verify=true");
  });
});
