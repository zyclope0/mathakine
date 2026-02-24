"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { api, ApiClientError } from "@/lib/api/client";
import { useTranslations } from "next-intl";
import type { User } from "@/types/api";

/** Redirection optionnelle après login (ex: /dashboard post-inscription) */
const postLoginRedirectRef = { current: null as string | null };

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string; // Optionnel car peut être dans les cookies
  user: User;
}

interface ForgotPasswordData {
  email: string;
}

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const t = useTranslations("toasts.auth");

  // Récupérer l'utilisateur actuel
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
        // Si 401 après refresh automatique, l'utilisateur n'est pas authentifié (normal)
        if (err instanceof ApiClientError && err.status === 401) {
          // Le refresh automatique a déjà été tenté par le client API
          // Si on arrive ici, c'est que le refresh a échoué ou qu'il n'y a pas de refresh token
          // Nettoyer le cache pour éviter d'utiliser des données obsolètes
          queryClient.setQueryData(["auth", "me"], null);
          return null;
        }
        throw err;
      }
    },
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
    // Utiliser les données en cache pendant la navigation côté client
    refetchOnMount: false,
    refetchOnWindowFocus: false,
  });

  // Connexion
  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const response = await api.post<TokenResponse>("/api/auth/login", credentials);
      return response;
    },
    onSuccess: async (data) => {
      // refresh_token uniquement en cookie HttpOnly (back) — jamais en localStorage (sécurité XSS)
      // Sync access_token sur le domaine frontend (cross-domain prod : backend cookie pas envoyé aux routes Next.js)
      // IMPORTANT : attendre la sync avant de naviguer, sinon le cookie peut manquer pour les flux SSE
      if (data.access_token && typeof window !== "undefined") {
        const { syncAccessTokenToFrontend } = await import("@/lib/api/client");
        await syncAccessTokenToFrontend(data.access_token);
      }

      // Mettre à jour le cache directement avec les données utilisateur reçues
      // Cela évite que ProtectedRoute redirige vers /login pendant le rechargement
      queryClient.setQueryData(["auth", "me"], data.user);
      toast.success(t("loginSuccess"), {
        description: `Bienvenue ${data.user.username} !`,
      });
      // Rediriger : onboarding si pas encore fait, sinon /dashboard (post-inscription) ou /exercises
      const needsOnboarding = !data.user.onboarding_completed_at;
      const target =
        needsOnboarding
          ? "/onboarding"
          : postLoginRedirectRef.current || "/exercises";
      postLoginRedirectRef.current = null;
      router.replace(target);
    },
    onError: (error: ApiClientError) => {
      let message: string;
      if (error.status === 403) {
        message = error.message || "Accès refusé.";
      } else if (error.status === 401) {
        message = "Nom d'utilisateur ou mot de passe incorrect";
      } else if (error.status === 400) {
        message = error.message || "Format de requête invalide";
      } else if (error.status === 500) {
        message = error.message || "Erreur serveur. Veuillez réessayer plus tard.";
      } else {
        message = error.message || t("loginError");
      }
      toast.error(t("loginError"), { description: message });
    },
  });

  // Inscription
  const registerMutation = useMutation({
    mutationFn: async (data: RegisterData) => {
      const response = await api.post<User>("/api/users/", data);
      return response;
    },
    onSuccess: async (data, variables) => {
      // Auto-login après inscription → onboarding si besoin, sinon dashboard
      postLoginRedirectRef.current = "/dashboard";
      try {
        await loginMutation.mutateAsync({
          username: variables.username,
          password: variables.password,
        });
        // login onSuccess gère toast + redirection vers /dashboard
      } catch {
        // Fallback si login échoue (rare) : rediriger vers login
        postLoginRedirectRef.current = null;
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

  // Déconnexion
  const logoutMutation = useMutation({
    mutationFn: async () => {
      try {
        await api.post("/api/auth/logout");
        // Effacer le cookie access_token du domaine frontend (cross-domain prod)
        if (typeof window !== "undefined") {
          await fetch("/api/auth/sync-cookie", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ clear: true }),
            credentials: "include",
          }).catch(() => {});
        }
      } catch {
        // Même en cas d'erreur, on déconnecte côté client
        // Ne pas logger en production pour éviter les fuites d'information
      }
    },
    onSuccess: () => {
      // Nettoyer l'ancien refresh_token du localStorage (rétro-compat sessions pré-migration)
      if (typeof window !== "undefined") {
        try {
          localStorage.removeItem("refresh_token");
        } catch {
          /* ignore */
        }
      }
      toast.success(t("logoutSuccess"));
      // Nettoyer le cache
      queryClient.clear();
      // Rediriger vers la page d'accueil
      router.push("/");
    },
  });

  // Mot de passe oublié
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
