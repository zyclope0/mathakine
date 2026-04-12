"use client";

/**
 * useAdminUsersPageController — état local, filtres, pagination et handlers
 * pour la page admin utilisateurs (ACTIF-06-ADMIN-USERS-01).
 *
 * Aucun fetch direct : délègue à useAdminUsers. Pas de JSX.
 */

import { useCallback, useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { toast } from "sonner";
import type { AdminUser } from "@/hooks/useAdminUsers";
import { useAdminUsers } from "@/hooks/useAdminUsers";
import { useAuth } from "@/hooks/useAuth";
import { normalizeUserRole, type UserRole } from "@/lib/auth/userRoles";

export const PAGE_SIZE = 20;

const ROLE_VALUES = ["all", "apprenant", "enseignant", "moderateur", "admin"] as const;

function localeTag(locale: string): string {
  return locale === "en" ? "en-US" : "fr-FR";
}

export function useAdminUsersPageController() {
  const t = useTranslations("adminPages.users");
  const tToast = useTranslations("adminPages.users.toast");
  const locale = useLocale();
  const dateLocale = useMemo(() => localeTag(locale), [locale]);

  const [search, setSearch] = useState("");
  const [role, setRole] = useState<UserRole | "all">("all");
  const [isActiveFilter, setIsActiveFilter] = useState<string>("all");
  const [page, setPage] = useState(0);
  const [roleEditUser, setRoleEditUser] = useState<AdminUser | null>(null);
  const [roleEditValue, setRoleEditValue] = useState<UserRole>("apprenant");
  const [deleteConfirmUser, setDeleteConfirmUser] = useState<AdminUser | null>(null);

  const isActive = isActiveFilter === "all" ? undefined : isActiveFilter === "true";

  const { user: currentUser } = useAuth();
  const {
    users,
    total,
    isLoading,
    error,
    updateUserActive,
    updateUserRole,
    sendResetPassword,
    resendVerification,
    deleteUser,
    isUpdating,
    isSendingReset,
    isResendingVerification,
    isDeleting,
  } = useAdminUsers({
    ...(search && { search }),
    ...(role !== "all" && { role }),
    ...(isActive !== undefined && { is_active: isActive }),
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
  });

  const roles = useMemo(
    () =>
      ROLE_VALUES.map((value) => ({
        value,
        label: t(`roles.${value}`),
      })),
    [t]
  );

  const roleLabel = useCallback(
    (roleValue: string) => {
      const n = normalizeUserRole(roleValue);
      if (!n) return roleValue;
      return t(`roles.${n}`);
    },
    [t]
  );

  const setSearchQuery = useCallback((value: string) => {
    setSearch(value);
    setPage(0);
  }, []);

  const setRoleFilter = useCallback((value: UserRole | "all") => {
    setRole(value);
    setPage(0);
  }, []);

  const setStatusFilter = useCallback((value: string) => {
    setIsActiveFilter(value);
    setPage(0);
  }, []);

  const openRoleEditor = useCallback((u: AdminUser) => {
    setRoleEditUser(u);
    setRoleEditValue(normalizeUserRole(u.role) ?? "apprenant");
  }, []);

  const closeRoleDialog = useCallback(() => {
    setRoleEditUser(null);
  }, []);

  const closeDeleteDialog = useCallback(() => {
    setDeleteConfirmUser(null);
  }, []);

  const handleToggleActive = useCallback(
    async (u: { id: number; username: string; is_active: boolean }) => {
      try {
        await updateUserActive({ userId: u.id, isActive: !u.is_active });
        toast.success(u.is_active ? tToast("deactivated") : tToast("reactivated"), {
          description: u.is_active
            ? tToast("deactivatedDesc", { username: u.username })
            : tToast("reactivatedDesc", { username: u.username }),
        });
      } catch (err) {
        const msg = err instanceof Error ? err.message : tToast("updateFailed");
        toast.error(tToast("errorTitle"), { description: msg });
      }
    },
    [updateUserActive, tToast]
  );

  const handleUpdateRole = useCallback(
    async (u: AdminUser, newRole: UserRole) => {
      try {
        await updateUserRole({ userId: u.id, role: newRole });
        toast.success(tToast("roleChanged"), {
          description: tToast("roleChangedDesc", {
            username: u.username,
            role: roleLabel(newRole),
          }),
        });
        setRoleEditUser(null);
      } catch (err) {
        const msg = err instanceof Error ? err.message : tToast("updateFailed");
        toast.error(tToast("errorTitle"), { description: msg });
      }
    },
    [updateUserRole, tToast, roleLabel]
  );

  const handleSendResetPassword = useCallback(
    async (u: AdminUser) => {
      try {
        await sendResetPassword(u.id);
        toast.success(tToast("emailSent"), {
          description: tToast("resetDesc", { email: u.email }),
        });
      } catch (err) {
        const msg = err instanceof Error ? err.message : tToast("sendFailed");
        toast.error(tToast("errorTitle"), { description: msg });
      }
    },
    [sendResetPassword, tToast]
  );

  const handleResendVerification = useCallback(
    async (u: AdminUser) => {
      try {
        await resendVerification(u.id);
        toast.success(tToast("emailSent"), {
          description: tToast("verifyDesc", { email: u.email }),
        });
      } catch (err) {
        const msg = err instanceof Error ? err.message : tToast("sendFailed");
        toast.error(tToast("errorTitle"), { description: msg });
      }
    },
    [resendVerification, tToast]
  );

  const handleDeleteUser = useCallback(
    async (u: AdminUser) => {
      try {
        await deleteUser(u.id);
        toast.success(tToast("userDeleted"), {
          description: tToast("userDeletedDesc", { username: u.username }),
        });
        setDeleteConfirmUser(null);
      } catch (err) {
        const msg = err instanceof Error ? err.message : tToast("deleteFailed");
        toast.error(tToast("errorTitle"), { description: msg });
      }
    },
    [deleteUser, tToast]
  );

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;
  const hasNext = page < totalPages - 1;
  const hasPrev = page > 0;

  return {
    t,
    dateLocale,
    roles,
    roleLabel,
    search,
    setSearchQuery,
    role,
    setRoleFilter,
    isActiveFilter,
    setStatusFilter,
    page,
    setPage,
    roleEditUser,
    roleEditValue,
    setRoleEditValue,
    deleteConfirmUser,
    setDeleteConfirmUser,
    openRoleEditor,
    closeRoleDialog,
    closeDeleteDialog,
    users,
    total,
    isLoading,
    error,
    currentUser,
    isUpdating,
    isSendingReset,
    isResendingVerification,
    isDeleting,
    handleToggleActive,
    handleUpdateRole,
    handleSendResetPassword,
    handleResendVerification,
    handleDeleteUser,
    totalPages,
    hasNext,
    hasPrev,
  };
}
