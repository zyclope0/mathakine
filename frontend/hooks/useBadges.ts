'use client';

import { useMemo, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiClientError } from '@/lib/api/client';
import type { UserBadgesResponse, GamificationStats, Badge, UserBadge } from '@/types/api';
import { toast } from 'sonner';
import { useLocaleStore } from '@/lib/stores/localeStore';

export function useBadges() {
  const queryClient = useQueryClient();
  const { locale } = useLocaleStore();

  // Invalider les queries quand la locale change
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ['badges'] });
  }, [locale, queryClient]);

  // Récupérer les badges de l'utilisateur
  const { data: userBadges, isLoading, error } = useQuery<UserBadgesResponse, ApiClientError>({
    queryKey: ['badges', 'user', locale], // Inclure la locale dans la queryKey
    queryFn: async () => {
      return await api.get<UserBadgesResponse>('/api/badges/user');
    },
    staleTime: 60 * 1000, // 1 minute
    // Utiliser les données en cache pendant la navigation côté client
    refetchOnMount: false,
    refetchOnWindowFocus: false,
  });

  // Récupérer tous les badges disponibles
  const { data: availableBadges } = useQuery<{ success: boolean; data: Badge[] }, ApiClientError>({
    queryKey: ['badges', 'available', locale], // Inclure la locale dans la queryKey
    queryFn: async () => {
      return await api.get<{ success: boolean; data: Badge[] }>('/api/badges/available');
    },
    staleTime: 5 * 60 * 1000, // 5 minutes (changent rarement)
  });

  // Récupérer les statistiques de gamification
  const { data: gamificationStats } = useQuery<{ success: boolean; data: GamificationStats }, ApiClientError>({
    queryKey: ['badges', 'stats'],
    queryFn: async () => {
      return await api.get<{ success: boolean; data: GamificationStats }>('/api/badges/stats');
    },
    staleTime: 30 * 1000, // 30 secondes
  });

  // Vérification forcée des badges
  const checkBadgesMutation = useMutation({
    mutationFn: async () => {
      return await api.post<{ success: boolean; new_badges: Badge[]; badges_earned: number; message: string }>('/api/badges/check');
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['badges'] });
      queryClient.invalidateQueries({ queryKey: ['user', 'stats'] });
      
      // Les toasts seront traduits côté composant si nécessaire
      // Pour l'instant, garder les messages en français comme fallback
      if (data.new_badges && data.new_badges.length > 0) {
        data.new_badges.forEach((badge) => {
          toast.success(`Nouveau badge débloqué ! 🎖️`, {
            description: `${badge.name}${badge.star_wars_title ? ` - ${badge.star_wars_title}` : ''}`,
            duration: 5000,
          });
        });
      } else {
        toast.info('Aucun nouveau badge', {
          description: 'Continuez vos efforts pour débloquer de nouveaux badges !',
        });
      }
    },
    onError: (error: ApiClientError) => {
      toast.error('Erreur', {
        description: error.message || 'Impossible de vérifier les badges.',
      });
    },
  });

  // Combiner les badges obtenus et disponibles pour avoir la liste complète
  const allBadges = useMemo(() => {
    const earned = userBadges?.data?.earned_badges || [];
    const available = availableBadges?.data || [];
    
    // Créer un map des badges obtenus par ID
    const earnedMap = new Map<number, UserBadge>();
    earned.forEach(eb => {
      // Les badges obtenus ont les mêmes propriétés qu'un Badge
      earnedMap.set(eb.id, eb as unknown as UserBadge);
    });
    
    // Combiner : badges disponibles + badges obtenus non dans la liste disponible
    const allBadgesList: Badge[] = [...available];
    earned.forEach(eb => {
      if (!available.find(ab => ab.id === eb.id)) {
        // Convertir UserBadge en Badge
        const badgeToAdd: Badge = {
          id: eb.id,
          code: eb.code,
          name: eb.name ?? null,
          category: eb.category ?? null,
          difficulty: eb.difficulty ?? null,
          points_reward: eb.points_reward ?? null,
          is_active: true,
          created_at: eb.earned_at ?? null,
        };
        if (eb.description !== undefined) {
          badgeToAdd.description = eb.description;
        }
        if (eb.star_wars_title !== undefined) {
          badgeToAdd.star_wars_title = eb.star_wars_title;
        }
        allBadgesList.push(badgeToAdd);
      }
    });
    
    return allBadgesList;
  }, [userBadges?.data?.earned_badges, availableBadges?.data]);

  return {
    earnedBadges: userBadges?.data?.earned_badges || [],
    availableBadges: allBadges,
    userStats: userBadges?.data?.user_stats,
    gamificationStats: gamificationStats?.data,
    isLoading,
    error,
    checkBadges: checkBadgesMutation.mutateAsync,
    isChecking: checkBadgesMutation.isPending,
  };
}

