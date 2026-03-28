"use client";

import { useMemo, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { api, ApiClientError } from "@/lib/api/client";
import type { UserBadgesResponse, GamificationStats, Badge, UserBadge } from "@/types/api";
import { readBadgeThematicTitleRaw } from "@/lib/gamification/badgeThematicTitle";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { useLocaleStore } from "@/lib/stores/localeStore";

export function useBadges() {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { locale } = useLocaleStore();
  const t = useTranslations("toasts");

  // Invalider les queries quand la locale change
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ["badges"] });
  }, [locale, queryClient]);

  // Récupérer les badges de l'utilisateur
  const {
    data: userBadges,
    isLoading,
    error,
  } = useQuery<UserBadgesResponse, ApiClientError>({
    queryKey: ["badges", "user", locale], // Inclure la locale dans la queryKey
    queryFn: async () => {
      return await api.get<UserBadgesResponse>("/api/badges/user");
    },
    staleTime: 60 * 1000, // 1 minute
    // Utiliser les données en cache pendant la navigation côté client
    refetchOnMount: false,
    refetchOnWindowFocus: false,
  });

  // Récupérer tous les badges disponibles
  const { data: availableBadges } = useQuery<{ success: boolean; data: Badge[] }, ApiClientError>({
    queryKey: ["badges", "available", locale], // Inclure la locale dans la queryKey
    queryFn: async () => {
      return await api.get<{ success: boolean; data: Badge[] }>("/api/badges/available");
    },
    staleTime: 5 * 60 * 1000, // 5 minutes (changent rarement)
  });

  // Récupérer les statistiques de gamification
  const { data: gamificationStats } = useQuery<
    { success: boolean; data: GamificationStats },
    ApiClientError
  >({
    queryKey: ["badges", "stats"],
    queryFn: async () => {
      return await api.get<{ success: boolean; data: GamificationStats }>("/api/badges/stats");
    },
    staleTime: 30 * 1000, // 30 secondes
  });

  // A-4 : Stats rareté par badge (preuve sociale, « X% ont débloqué »)
  const { data: rarityData } = useQuery<
    {
      success: boolean;
      data: {
        total_users: number;
        by_badge: Record<string, { unlock_count: number; unlock_percent: number; rarity: string }>;
      };
    },
    ApiClientError
  >({
    queryKey: ["badges", "rarity"],
    queryFn: async () => {
      return await api.get<{
        success: boolean;
        data: {
          total_users: number;
          by_badge: Record<
            string,
            { unlock_count: number; unlock_percent: number; rarity: string }
          >;
        };
      }>("/api/badges/rarity");
    },
    staleTime: 5 * 60 * 1000, // 5 min (cache)
  });

  // Vérification forcée des badges
  const checkBadgesMutation = useMutation({
    mutationFn: async () => {
      return await api.post<{
        success: boolean;
        new_badges: Badge[];
        badges_earned: number;
        message: string;
      }>("/api/badges/check");
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["badges"] });
      queryClient.invalidateQueries({ queryKey: ["user", "stats"] });

      // Les toasts seront traduits côté composant si nécessaire
      // Pour l'instant, garder les messages en français comme fallback
      if (data.new_badges && data.new_badges.length > 0) {
        data.new_badges.forEach((badge) => {
          const subtitle = readBadgeThematicTitleRaw(badge);
          toast.success(t("badges.newBadgeUnlocked"), {
            description: `${badge.name}${subtitle ? ` - ${subtitle}` : ""}`,
            duration: 6000,
            icon: "🎖️",
          });
        });
      } else {
        toast.info(t("badges.noBadge"), {
          description: t("badges.noBadgeDescription"),
        });
      }
    },
    onError: (error: ApiClientError) => {
      if (error.status === 401) {
        queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
        router.push("/login");
        return;
      }
      toast.error(t("badges.checkError"), {
        description: error.message || t("badges.checkErrorDescription"),
      });
    },
  });

  // Combiner les badges obtenus et disponibles pour avoir la liste complète
  const allBadges = useMemo(() => {
    const earned = userBadges?.data?.earned_badges || [];
    const available = availableBadges?.data || [];

    // Créer un map des badges obtenus par ID
    const earnedMap = new Map<number, UserBadge>();
    earned.forEach((eb) => {
      // Les badges obtenus ont les mêmes propriétés qu'un Badge
      earnedMap.set(eb.id, eb as unknown as UserBadge);
    });

    // Combiner : badges disponibles + badges obtenus non dans la liste disponible
    const allBadgesList: Badge[] = [...available];
    earned.forEach((eb) => {
      if (!available.find((ab) => ab.id === eb.id)) {
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
        if (eb.thematic_title !== undefined) {
          badgeToAdd.thematic_title = eb.thematic_title;
        }
        if (eb.star_wars_title !== undefined) {
          badgeToAdd.star_wars_title = eb.star_wars_title;
        }
        allBadgesList.push(badgeToAdd);
      }
    });

    return allBadgesList;
  }, [userBadges?.data?.earned_badges, availableBadges?.data]);

  const rarityMap = useMemo(() => rarityData?.data?.by_badge ?? {}, [rarityData]);

  const pinnedBadgeIds = useMemo(
    () =>
      (userBadges?.data?.user_stats as { pinned_badge_ids?: number[] } | undefined)
        ?.pinned_badge_ids ?? [],
    [userBadges?.data?.user_stats]
  );

  const pinBadgesMutation = useMutation({
    mutationFn: async (badgeIds: number[]) => {
      return await api.patch<{ success: boolean; data: { pinned_badge_ids: number[] } }>(
        "/api/badges/pin",
        { badge_ids: badgeIds }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["badges"] });
    },
  });

  return {
    earnedBadges: userBadges?.data?.earned_badges || [],
    availableBadges: allBadges,
    userStats: userBadges?.data?.user_stats,
    gamificationStats: gamificationStats?.data,
    rarityMap,
    pinnedBadgeIds,
    pinBadges: pinBadgesMutation.mutateAsync,
    isLoading,
    error,
    checkBadges: checkBadgesMutation.mutateAsync,
    isChecking: checkBadgesMutation.isPending,
  };
}
