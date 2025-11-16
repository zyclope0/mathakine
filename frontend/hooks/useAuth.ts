'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { api, ApiClientError } from '@/lib/api/client';
import { useTranslations } from 'next-intl';
import type { User } from '@/types/api';

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
  user: User;
}

interface ForgotPasswordData {
  email: string;
}

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const t = useTranslations('toasts.auth');

  // Récupérer l'utilisateur actuel
  const { data: user, isLoading, error, isFetching } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      try {
        return await api.get<User>('/api/users/me');
      } catch (err) {
        // Si 401 après refresh automatique, l'utilisateur n'est pas authentifié (normal)
        if (err instanceof ApiClientError && err.status === 401) {
          // Le refresh automatique a déjà été tenté par le client API
          // Si on arrive ici, c'est que le refresh a échoué ou qu'il n'y a pas de refresh token
          // Nettoyer le cache pour éviter d'utiliser des données obsolètes
          queryClient.setQueryData(['auth', 'me'], null);
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
      const response = await api.post<TokenResponse>('/api/auth/login', credentials);
      return response;
    },
    onSuccess: (data) => {
      // Mettre à jour le cache directement avec les données utilisateur reçues
      // Cela évite que ProtectedRoute redirige vers /login pendant le rechargement
      queryClient.setQueryData(['auth', 'me'], data.user);
      toast.success(t('loginSuccess'), {
        description: `Bienvenue ${data.user.username} !`,
      });
      // Rediriger vers la page d'exercices (fonctionnalité principale)
      // Utiliser replace pour éviter d'ajouter /login dans l'historique
      router.replace('/exercises');
    },
    onError: (error: ApiClientError) => {
      let message: string;
      if (error.status === 401) {
        message = 'Nom d\'utilisateur ou mot de passe incorrect';
      } else if (error.status === 400) {
        message = error.message || 'Format de requête invalide';
      } else if (error.status === 500) {
        message = error.message || 'Erreur serveur. Veuillez réessayer plus tard.';
      } else {
        message = error.message || t('loginError');
      }
      toast.error(t('loginError'), {
        description: message,
      });
    },
  });

  // Inscription
  const registerMutation = useMutation({
    mutationFn: async (data: RegisterData) => {
      const response = await api.post<User>('/api/users/', data);
      return response;
    },
    onSuccess: () => {
      toast.success(t('registerSuccess'), {
        description: 'Vous pouvez maintenant vous connecter.',
      });
      // Après inscription, rediriger vers login
      router.push('/login?registered=true');
    },
    onError: (error: ApiClientError) => {
      const message = error.status === 409
        ? 'Ce nom d\'utilisateur ou email est déjà utilisé'
        : error.message || t('registerError');
      toast.error(t('registerError'), {
        description: message,
      });
    },
  });

  // Déconnexion
  const logoutMutation = useMutation({
    mutationFn: async () => {
      try {
        await api.post('/api/auth/logout');
      } catch (error) {
        // Même en cas d'erreur, on déconnecte côté client
        // Ne pas logger en production pour éviter les fuites d'information
      }
    },
    onSuccess: () => {
      toast.success(t('logoutSuccess'));
      // Nettoyer le cache
      queryClient.clear();
      // Rediriger vers la page d'accueil
      router.push('/');
    },
  });

  // Mot de passe oublié
  const forgotPasswordMutation = useMutation({
    mutationFn: async (data: ForgotPasswordData) => {
      await api.post('/api/auth/forgot-password', data);
    },
    onSuccess: () => {
      toast.success(t('forgotPasswordSuccess'), {
        description: 'Si un compte existe avec cette adresse, vous recevrez un lien de réinitialisation.',
      });
    },
    onError: (error: ApiClientError) => {
      toast.error(t('forgotPasswordError'), {
        description: error.message || 'Impossible d\'envoyer l\'email',
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

