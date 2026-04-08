"use client";

import * as Sentry from "@sentry/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { api, ApiClientError } from "@/lib/api/client";
import {
  clearFrontendAuthSyncCookie,
  syncAccessTokenToFrontend,
  syncCsrfTokenToFrontend,
} from "@/lib/auth/auth-session-sync";
import {
  isAuthMeQueryUnauthenticatedError,
  resolveLoginErrorDescription,
} from "@/lib/auth/authLoginFlow";
import {
  clearPostLoginRedirectOverride,
  consumePostLoginRedirectOverride,
  setPostLoginRedirectOverride,
} from "@/lib/auth/postLoginRedirect";
import { getDefaultPostLoginRoute } from "@/lib/auth/userRoles";
import type {
  ForgotPasswordData,
  LoginCredentials,
  RegisterData,
  TokenResponse,
} from "@/lib/auth/types";
import { useTranslations } from "next-intl";
import type { User } from "@/types/api";

export type {
  ForgotPasswordData,
  LoginCredentials,
  RegisterData,
  TokenResponse,
} from "@/lib/auth/types";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const t = useTranslations("toasts.auth");

  const {
    data: user,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      try {
        return await api.get<User>("/api/users/me");
      } catch (err) {
        if (isAuthMeQueryUnauthenticatedError(err)) {
          queryClient.setQueryData(["auth", "me"], null);
          return null;
        }
        throw err;
      }
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
  });

  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const response = await api.post<TokenResponse>("/api/auth/login", credentials);
      return response;
    },
    onSuccess: async (data) => {
      if (data.access_token && typeof window !== "undefined") {
        await syncAccessTokenToFrontend(data.access_token);
      }

      if (data.csrf_token && typeof window !== "undefined") {
        syncCsrfTokenToFrontend(data.csrf_token);
      }

      queryClient.setQueryData(["auth", "me"], data.user);

      Sentry.setUser({
        id: String(data.user.id),
        username: data.user.username,
      });

      toast.success(t("loginSuccess"), {
        description: t("loginWelcome", { username: data.user.username }),
      });

      const needsOnboarding = !data.user.onboarding_completed_at;
      const defaultTarget = getDefaultPostLoginRoute(data.user.role);
      let target: string;
      if (needsOnboarding) {
        clearPostLoginRedirectOverride();
        target = "/onboarding";
      } else {
        target = consumePostLoginRedirectOverride() || defaultTarget;
      }
      router.replace(target);
    },
    onError: (error: ApiClientError) => {
      const message = resolveLoginErrorDescription(error, {
        loginForbidden: t("loginForbidden"),
        loginInvalidCredentials: t("loginInvalidCredentials"),
        loginInvalidRequest: t("loginInvalidRequest"),
        loginServerError: t("loginServerError"),
        loginError: t("loginError"),
      });
      toast.error(t("loginError"), { description: message });
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterData) => {
      const response = await api.post<User>("/api/users/", data);
      return response;
    },
    onSuccess: async (_data, variables) => {
      setPostLoginRedirectOverride("/dashboard");
      try {
        await loginMutation.mutateAsync({
          username: variables.username,
          password: variables.password,
        });
      } catch {
        clearPostLoginRedirectOverride();
        toast.success(t("registerSuccess"), {
          description:
            "Un email de vérification a été envoyé. Veuillez vérifier votre boîte de réception.",
        });
        router.push("/login?registered=true&verify=true");
      }
    },
    onError: (error: ApiClientError) => {
      const message = error.message || t("registerError");
      toast.error(t("registerError"), {
        description: message,
      });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      try {
        await api.post("/api/auth/logout");
        if (typeof window !== "undefined") {
          await clearFrontendAuthSyncCookie();
        }
      } catch {
        // Même en cas d'erreur, on déconnecte côté client
      }
    },
    onSuccess: () => {
      if (typeof window !== "undefined") {
        try {
          localStorage.removeItem("refresh_token");
        } catch {
          /* ignore */
        }
      }
      Sentry.setUser(null);

      queryClient.setQueryData(["auth", "me"], null);
      toast.success(t("logoutSuccess"));
      queryClient.clear();
      router.replace("/");
      router.refresh();
    },
  });

  const forgotPasswordMutation = useMutation({
    mutationFn: async (data: ForgotPasswordData) => {
      await api.post("/api/auth/forgot-password", data);
    },
    onSuccess: () => {
      toast.success(t("forgotPasswordSuccess"), {
        description:
          "Si un compte existe avec cette adresse, vous recevrez un lien de réinitialisation.",
      });
    },
    onError: (error: ApiClientError) => {
      toast.error(t("forgotPasswordError"), {
        description: error.message || "Impossible d'envoyer l'email",
      });
    },
  });

  return {
    user: user ?? null,
    isLoading,
    isAuthenticated: !!user && !error,
    error,
    login: loginMutation.mutate,
    loginAsync: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    register: registerMutation.mutate,
    registerAsync: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    logout: logoutMutation.mutate,
    isLoggingOut: logoutMutation.isPending,
    forgotPassword: forgotPasswordMutation.mutate,
    forgotPasswordAsync: forgotPasswordMutation.mutateAsync,
    isForgotPasswordPending: forgotPasswordMutation.isPending,
  };
}
