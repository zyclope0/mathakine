/**
 * Unit tests for useAdminUsersPageController (ACTIF-06-ADMIN-USERS-01) —
 * filter → useAdminUsers params wiring and pagination; mocks useAdminUsers / useAuth / toasts.
 */

import type { ReactNode } from "react";
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import type { AdminUsersParams } from "@/hooks/useAdminUsers";
import { useAdminUsersPageController, PAGE_SIZE } from "@/hooks/useAdminUsersPageController";

const useAdminUsersSpy = vi.fn();

vi.mock("@/hooks/useAdminUsers", () => ({
  useAdminUsers: (params: AdminUsersParams) => useAdminUsersSpy(params),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({ user: { id: 1 } }),
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

function createWrapper() {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <NextIntlClientProvider locale="fr" messages={fr}>
        {children}
      </NextIntlClientProvider>
    );
  }
  return Wrapper;
}

const defaultHookReturn = {
  users: [] as never[],
  total: 100,
  isLoading: false,
  error: null,
  updateUserActive: vi.fn(),
  updateUserRole: vi.fn(),
  sendResetPassword: vi.fn(),
  resendVerification: vi.fn(),
  deleteUser: vi.fn(),
  isUpdating: false,
  isSendingReset: false,
  isResendingVerification: false,
  isDeleting: false,
};

describe("useAdminUsersPageController", () => {
  beforeEach(() => {
    useAdminUsersSpy.mockReset();
    useAdminUsersSpy.mockImplementation(() => ({ ...defaultHookReturn }));
  });

  it("passes skip 0 and limit PAGE_SIZE on initial mount", () => {
    renderHook(() => useAdminUsersPageController(), { wrapper: createWrapper() });
    expect(useAdminUsersSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        skip: 0,
        limit: PAGE_SIZE,
      })
    );
  });

  it("passes skip aligned with page index", () => {
    const { result } = renderHook(() => useAdminUsersPageController(), {
      wrapper: createWrapper(),
    });
    act(() => {
      result.current.setPage(2);
    });
    expect(useAdminUsersSpy).toHaveBeenLastCalledWith(
      expect.objectContaining({
        skip: 2 * PAGE_SIZE,
        limit: PAGE_SIZE,
      })
    );
  });

  it("resets page to 0 when search query changes", () => {
    const { result } = renderHook(() => useAdminUsersPageController(), {
      wrapper: createWrapper(),
    });
    act(() => {
      result.current.setPage(2);
    });
    act(() => {
      result.current.setSearchQuery("alice");
    });
    expect(useAdminUsersSpy).toHaveBeenLastCalledWith(
      expect.objectContaining({
        search: "alice",
        skip: 0,
        limit: PAGE_SIZE,
      })
    );
  });

  it("passes role filter when not all", () => {
    const { result } = renderHook(() => useAdminUsersPageController(), {
      wrapper: createWrapper(),
    });
    act(() => {
      result.current.setRoleFilter("admin");
    });
    expect(useAdminUsersSpy).toHaveBeenLastCalledWith(
      expect.objectContaining({
        role: "admin",
        skip: 0,
      })
    );
  });

  it("passes is_active when status filter is true or false", () => {
    const { result } = renderHook(() => useAdminUsersPageController(), {
      wrapper: createWrapper(),
    });
    act(() => {
      result.current.setStatusFilter("true");
    });
    expect(useAdminUsersSpy).toHaveBeenLastCalledWith(
      expect.objectContaining({
        is_active: true,
      })
    );
    act(() => {
      result.current.setStatusFilter("false");
    });
    expect(useAdminUsersSpy).toHaveBeenLastCalledWith(
      expect.objectContaining({
        is_active: false,
      })
    );
  });
});
