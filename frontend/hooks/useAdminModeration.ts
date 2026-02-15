"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

export interface ModerationExercise {
  id: number;
  title: string;
  exercise_type: string;
  age_group: string;
  is_archived: boolean;
  created_at: string | null;
}

export interface ModerationChallenge {
  id: number;
  title: string;
  challenge_type: string;
  age_group: string;
  is_archived: boolean;
  created_at: string | null;
}

export interface ModerationData {
  exercises: ModerationExercise[];
  challenges: ModerationChallenge[];
  total_exercises: number;
  total_challenges: number;
}

export function useAdminModeration(type: "exercises" | "challenges" | "all" = "all") {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin-moderation", type],
    queryFn: async () => {
      const res = await api.get<ModerationData>(
        `/api/admin/moderation?type=${encodeURIComponent(type)}`
      );
      return res;
    },
    staleTime: 30_000,
  });

  return {
    data: data ?? null,
    exercises: data?.exercises ?? [],
    challenges: data?.challenges ?? [],
    totalExercises: data?.total_exercises ?? 0,
    totalChallenges: data?.total_challenges ?? 0,
    isLoading,
    error,
    refetch,
  };
}
