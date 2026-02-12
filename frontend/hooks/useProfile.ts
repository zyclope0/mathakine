"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, ApiClientError } from "@/lib/api/client";
import { useTranslations } from "next-intl";
import type { User } from "@/types/api";

export interface ProfileUpdateData {
  email?: string;
  full_name?: string;
  grade_level?: number;
  learning_style?: string;
  preferred_difficulty?: string;
  preferred_theme?: string;
  accessibility_settings?: Record<string, boolean>;
}

export interface PasswordUpdateData {
  current_password: string;
  new_password: string;
}

export function useProfile() {
  const queryClient = useQueryClient();
  const t = useTranslations("toasts.profile");

  // Mise à jour du profil
  const updateProfileMutation = useMutation({
    mutationFn: async (data: ProfileUpdateData) => {
      return await api.put<User>("/api/users/me", data);
    },
    onSuccess: (updatedUser) => {
      // Mettre à jour le cache de l'utilisateur
      queryClient.setQueryData(["auth", "me"], updatedUser);
      toast.success(t("updateSuccess"), {
        description: t("updateSuccessDescription"),
      });
    },
    onError: (error: ApiClientError) => {
      const message =
        error.status === 400
          ? error.message || t("updateError")
          : error.status === 401
            ? t("unauthorized")
            : t("updateError");
      toast.error(t("updateError"), {
        description: message,
      });
    },
  });

  // Changement de mot de passe
  const changePasswordMutation = useMutation({
    mutationFn: async (data: PasswordUpdateData) => {
      return await api.put<{ message: string; success: boolean }>("/api/users/me/password", data);
    },
    onSuccess: () => {
      toast.success(t("passwordChangeSuccess"), {
        description: t("passwordChangeSuccessDescription"),
      });
    },
    onError: (error: ApiClientError) => {
      const message =
        error.status === 401
          ? t("passwordIncorrect")
          : error.status === 400
            ? error.message || t("passwordChangeError")
            : t("passwordChangeError");
      toast.error(t("passwordChangeError"), {
        description: message,
      });
    },
  });

  return {
    updateProfile: updateProfileMutation.mutate,
    updateProfileAsync: updateProfileMutation.mutateAsync,
    isUpdatingProfile: updateProfileMutation.isPending,
    changePassword: changePasswordMutation.mutate,
    changePasswordAsync: changePasswordMutation.mutateAsync,
    isChangingPassword: changePasswordMutation.isPending,
  };
}
