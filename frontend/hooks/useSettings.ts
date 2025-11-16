'use client';

import { useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { api, ApiClientError } from '@/lib/api/client';
import { useTranslations } from 'next-intl';
import type { User } from '@/types/api';

export interface SettingsUpdateData {
  language_preference?: string;
  timezone?: string;
  is_public_profile?: boolean;
  allow_friend_requests?: boolean;
  show_in_leaderboards?: boolean;
  data_retention_consent?: boolean;
  marketing_consent?: boolean;
}

export interface UserSession {
  id: number;
  device_info?: {
    browser?: string;
    os?: string;
    device?: string;
  };
  ip_address?: string;
  location_data?: {
    city?: string;
    country?: string;
  };
  last_activity: string;
  created_at: string;
  is_active: boolean;
}

export function useSettings() {
  const queryClient = useQueryClient();
  const t = useTranslations('settings.toasts');

  // Callback pour réinitialiser le flag de mise à jour (utilisé par le composant)
  const onUpdateSuccessCallbackRef = useRef<(() => void) | null>(null);

  // Mise à jour des paramètres
  const updateSettingsMutation = useMutation({
    mutationFn: async (data: SettingsUpdateData) => {
      return await api.put<User>('/api/users/me', data);
    },
    onSuccess: (updatedUser) => {
      // Mettre à jour le cache de l'utilisateur de manière optimiste
      // Utiliser une fonction pour éviter les références d'objets qui changent
      queryClient.setQueryData(['auth', 'me'], (old: User | undefined) => {
        if (!old) return updatedUser;
        // Fusionner les nouvelles données avec les anciennes pour éviter les pertes
        return { ...old, ...updatedUser };
      });
      toast.success(t('updateSuccess'), {
        description: t('updateSuccessDescription'),
      });
      // Réinitialiser le flag dans le composant après un court délai
      if (onUpdateSuccessCallbackRef.current) {
        setTimeout(() => {
          onUpdateSuccessCallbackRef.current?.();
        }, 500);
      }
    },
    onError: (error: ApiClientError) => {
      const message = error.status === 400
        ? error.message || t('updateError')
        : error.status === 401
        ? 'Non autorisé'
        : t('updateError');
      toast.error(t('updateError'), {
        description: message,
      });
    },
  });

  // Export de données
  const exportDataMutation = useMutation({
    mutationFn: async () => {
      const response = await api.get('/api/users/me/export');
      return response;
    },
    onSuccess: (data) => {
      // Créer un fichier JSON téléchargeable
      const jsonStr = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonStr], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mathakine-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast.success(t('exportSuccess'), {
        description: t('exportSuccessDescription'),
      });
    },
    onError: () => {
      toast.error(t('exportError'), {
        description: 'Une erreur est survenue lors de l\'export de vos données.',
      });
    },
  });

  // Suppression de compte
  const deleteAccountMutation = useMutation({
    mutationFn: async () => {
      return await api.delete<{ message: string }>('/api/users/me');
    },
    onSuccess: () => {
      toast.success(t('deleteSuccess'), {
        description: t('deleteSuccessDescription'),
      });
      // Rediriger vers la page d'accueil après suppression
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);
    },
    onError: () => {
      toast.error(t('deleteError'), {
        description: 'Une erreur est survenue lors de la suppression de votre compte.',
      });
    },
  });

  // Récupération des sessions (pour l'instant, retourner un tableau vide)
  // Les endpoints seront créés plus tard
  const getSessions = async (): Promise<UserSession[]> => {
    try {
      // TODO: Créer l'endpoint /api/users/me/sessions
      return [];
    } catch {
      return [];
    }
  };

  // Révoquer une session
  const revokeSessionMutation = useMutation({
    mutationFn: async (sessionId: number) => {
      // TODO: Créer l'endpoint /api/users/me/sessions/{sessionId}
      return await api.delete(`/api/users/me/sessions/${sessionId}`);
    },
    onSuccess: () => {
      toast.success(t('sessionRevoked'), {
        description: t('sessionRevokedDescription'),
      });
      // Rafraîchir les sessions
      queryClient.invalidateQueries({ queryKey: ['settings', 'sessions'] });
    },
    onError: () => {
      toast.error('Erreur', {
        description: 'Impossible de révoquer la session.',
      });
    },
  });

  return {
    updateSettings: updateSettingsMutation.mutate,
    updateSettingsAsync: updateSettingsMutation.mutateAsync,
    isUpdatingSettings: updateSettingsMutation.isPending,
    setOnUpdateSuccess: (callback: () => void) => {
      onUpdateSuccessCallbackRef.current = callback;
    },
    exportData: exportDataMutation.mutate,
    exportDataAsync: exportDataMutation.mutateAsync,
    isExportingData: exportDataMutation.isPending,
    deleteAccount: deleteAccountMutation.mutate,
    deleteAccountAsync: deleteAccountMutation.mutateAsync,
    isDeletingAccount: deleteAccountMutation.isPending,
    getSessions,
    revokeSession: revokeSessionMutation.mutate,
    isRevokingSession: revokeSessionMutation.isPending,
  };
}

