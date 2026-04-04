"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import { normalizeUserRole, type UserRole } from "@/lib/auth/userRoles";

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  is_email_verified?: boolean;
  created_at: string | null;
}

export interface AdminUsersParams {
  search?: string;
  role?: UserRole;
  is_active?: boolean;
  skip?: number;
  limit?: number;
}

export interface AdminUsersResponse {
  items: AdminUser[];
  total: number;
}

function normalizeAdminUser(user: AdminUser): AdminUser {
  return {
    ...user,
    role: normalizeUserRole(user.role) ?? "apprenant",
  };
}

export function useAdminUsers(params: AdminUsersParams = {}) {
  const { search = "", role, is_active, skip = 0, limit = 20 } = params;

  const searchParams = new URLSearchParams();
  if (search) searchParams.set("search", search);
  if (role) searchParams.set("role", role);
  if (is_active !== undefined) searchParams.set("is_active", String(is_active));
  searchParams.set("skip", String(skip));
  searchParams.set("limit", String(limit));

  const queryString = searchParams.toString();
  const url = `/api/admin/users${queryString ? `?${queryString}` : ""}`;

  const { data, isLoading, error, refetch } = useQuery<AdminUsersResponse, ApiClientError>({
    queryKey: ["admin", "users", { search, role, is_active, skip, limit }],
    queryFn: async () => {
      const response = await api.get<AdminUsersResponse>(url);
      return {
        ...response,
        items: response.items.map(normalizeAdminUser),
      };
    },
    staleTime: 30 * 1000,
  });

  const queryClient = useQueryClient();
  const patchMutation = useMutation({
    mutationFn: async ({
      userId,
      isActive,
      role,
    }: {
      userId: number;
      isActive?: boolean;
      role?: UserRole;
    }) => {
      const body: Record<string, unknown> = {};
      if (isActive !== undefined) body.is_active = isActive;
      if (role !== undefined) body.role = role;
      return api.patch<{ id: number; username: string; is_active: boolean; role: UserRole }>(
        `/api/admin/users/${userId}`,
        body as { is_active?: boolean; role?: string }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
    },
  });

  const sendResetMutation = useMutation({
    mutationFn: (userId: number) =>
      api.post<{ message: string }>(`/api/admin/users/${userId}/send-reset-password`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
  });

  const resendVerificationMutation = useMutation({
    mutationFn: (userId: number) =>
      api.post<{ message: string }>(`/api/admin/users/${userId}/resend-verification`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
  });

  const deleteUserMutation = useMutation({
    mutationFn: (userId: number) => api.delete<{ message: string }>(`/api/admin/users/${userId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
  });

  return {
    users: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading,
    error,
    refetch,
    updateUserActive: (params: { userId: number; isActive: boolean }) =>
      patchMutation.mutateAsync({ ...params, isActive: params.isActive }),
    updateUserRole: (params: { userId: number; role: UserRole }) =>
      patchMutation.mutateAsync({ userId: params.userId, role: params.role }),
    sendResetPassword: sendResetMutation.mutateAsync,
    resendVerification: resendVerificationMutation.mutateAsync,
    deleteUser: deleteUserMutation.mutateAsync,
    isUpdating: patchMutation.isPending,
    isSendingReset: sendResetMutation.isPending,
    isResendingVerification: resendVerificationMutation.isPending,
    isDeleting: deleteUserMutation.isPending,
    updateError: patchMutation.error,
  };
}
