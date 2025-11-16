'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { api, ApiClientError } from '@/lib/api/client';
import type { Challenge } from '@/types/api';
import { useLocaleStore } from '@/lib/stores/localeStore';

export function useChallenge(challengeId: number) {
  const queryClient = useQueryClient();
  const { locale } = useLocaleStore();

  // Invalider les queries quand la locale change
  useEffect(() => {
    if (challengeId > 0) {
      queryClient.invalidateQueries({ queryKey: ['challenge', challengeId] });
    }
  }, [locale, challengeId, queryClient]);

  const { data: challenge, isLoading, error } = useQuery<Challenge, ApiClientError>({
    queryKey: ['challenge', challengeId, locale], // Inclure la locale dans la queryKey
    queryFn: async () => {
      return await api.get<Challenge>(`/api/challenges/${challengeId}`);
    },
    enabled: !!challengeId && challengeId > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    challenge,
    isLoading,
    error,
  };
}

