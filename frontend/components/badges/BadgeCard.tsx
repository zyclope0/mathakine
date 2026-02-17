"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations, useLocale } from "next-intl";
import { Badge as BadgeComponent } from "@/components/ui/badge";
import { Trophy, Lock, CheckCircle, Pin, PinOff } from "lucide-react";
import type { Badge, UserBadge } from "@/types/api";
import { cn } from "@/lib/utils/cn";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";

interface BadgeProgress {
  current: number;
  target: number;
  progress: number;
}

interface RarityInfo {
  unlock_count: number;
  unlock_percent: number;
  rarity: string;
}

interface BadgeCardProps {
  badge: Badge;
  userBadge?: UserBadge | null;
  isEarned: boolean;
  progress?: BadgeProgress | null;
  index?: number;
  rarity?: RarityInfo | null;
  isPinned?: boolean;
  onTogglePin?: (badgeId: number) => void;
  canPin?: boolean;
}

const defaultDifficultyColor = {
  bg: "bg-amber-500/20",
  text: "text-amber-400",
  border: "border-amber-500/30",
};

const difficultyColors: Record<string, { bg: string; text: string; border: string }> = {
  bronze: defaultDifficultyColor,
  silver: {
    bg: "bg-gray-400/20",
    text: "text-gray-300",
    border: "border-gray-400/30",
  },
  gold: {
    bg: "bg-yellow-500/20",
    text: "text-yellow-400",
    border: "border-yellow-500/30",
  },
  legendary: {
    bg: "bg-amber-400/25",
    text: "text-amber-300",
    border: "border-amber-400/40",
  },
};

const categoryIcons: Record<string, string> = {
  progression: "📈",
  mastery: "⭐",
  special: "✨",
};

export function BadgeCard({
  badge,
  userBadge,
  isEarned,
  progress,
  index = 0,
  rarity,
  isPinned,
  onTogglePin,
  canPin,
}: BadgeCardProps) {
  const t = useTranslations("badges");
  const locale = useLocale();
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  const getDifficultyColor = (
    difficulty: string | null | undefined
  ): { bg: string; text: string; border: string } => {
    if (!difficulty) return defaultDifficultyColor;
    const color = difficultyColors[difficulty];
    if (color) {
      return color;
    }
    return defaultDifficultyColor;
  };

  const getCategoryIcon = (category: string | null | undefined): string => {
    if (!category) return "🏆";
    const icon = categoryIcons[category];
    return icon ?? "🏆";
  };

  const difficultyColor = getDifficultyColor(badge.difficulty);
  const categoryIcon = getCategoryIcon(badge.category);

  // Variantes d'animation avec garde-fous
  const variants = createVariants({
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  });

  const transition = createTransition({
    duration: 0.3,
    delay: index * 0.05,
  });

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={transition}
      className="h-full"
    >
      <Card
        className={cn(
          "card-spatial-depth relative overflow-hidden transition-all duration-300 h-full flex flex-col",
          isEarned
            ? "border-primary/50 shadow-lg shadow-primary/20 hover:scale-105"
            : "opacity-75 border-muted hover:opacity-90",
          // P3-12 : hiérarchie visuelle or/légendaire
          badge.difficulty === "gold" && "border-yellow-500/50 shadow-lg shadow-yellow-500/15",
          badge.difficulty === "legendary" &&
            "border-amber-400/60 ring-2 ring-amber-400/30 shadow-lg shadow-amber-400/20"
        )}
        role="article"
        aria-label={`Badge ${badge.name}${isEarned ? " obtenu" : " verrouillé"}`}
      >
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg md:text-xl flex items-center gap-2 font-bold">
                <span className="text-3xl shrink-0" aria-hidden="true">
                  {categoryIcon}
                </span>
                <span className="break-words">{badge.name || badge.code || "Badge sans nom"}</span>
              </CardTitle>
              {badge.star_wars_title && (
                <CardDescription className="mt-2 text-primary-on-dark italic text-sm">
                  {badge.star_wars_title}
                </CardDescription>
              )}
            </div>
            {/* Status + rareté + difficulté — alignés sans chevauchement */}
            <div className="flex items-center gap-2 shrink-0 flex-wrap justify-end">
              {isEarned ? (
                <>
                  {canPin && onTogglePin && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        onTogglePin(badge.id);
                      }}
                      className={cn(
                        "p-1.5 rounded-md transition-colors shrink-0",
                        isPinned
                          ? "bg-amber-500/30 text-amber-400"
                          : "text-muted-foreground hover:bg-muted hover:text-foreground"
                      )}
                      aria-label={isPinned ? t("unpin") : t("pin")}
                      title={isPinned ? t("unpin") : t("pin")}
                    >
                      {isPinned ? (
                        <PinOff className="h-4 w-4" aria-hidden="true" />
                      ) : (
                        <Pin className="h-4 w-4" aria-hidden="true" />
                      )}
                    </button>
                  )}
                  <CheckCircle className="h-5 w-5 text-green-500 shrink-0" aria-hidden="true" />
                </>
              ) : (
                <Lock className="h-5 w-5 text-muted-foreground/60 shrink-0" aria-label="Badge verrouillé" />
              )}
              {rarity && rarity.rarity === "rare" && (
                <BadgeComponent
                  variant="outline"
                  className="border-amber-500/50 bg-amber-500/20 text-amber-400 text-xs font-medium shrink-0"
                  aria-label={t("rarity.rare")}
                >
                  ✨ {t("rarity.rare")}
                </BadgeComponent>
              )}
              <BadgeComponent
                variant="outline"
                className={cn(
                  "badge-sweep shrink-0 text-sm",
                  difficultyColor.bg,
                  difficultyColor.text,
                  difficultyColor.border
                )}
                aria-label={`Difficulté: ${badge.difficulty}`}
              >
                {badge.difficulty === "bronze" && "🥉"}
                {badge.difficulty === "silver" && "🥈"}
                {badge.difficulty === "gold" && "🥇"}
                {badge.difficulty === "legendary" && "💎"}
              </BadgeComponent>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4 flex-1 flex flex-col min-h-0">
          {badge.description ? (
            <p className="text-sm md:text-base text-muted-foreground leading-relaxed line-clamp-3">
              {badge.description}
            </p>
          ) : (
            <p className="text-sm md:text-base text-muted-foreground/60 italic leading-relaxed line-clamp-3">
              Description non disponible
            </p>
          )}

          {/* A-4 : Preuve sociale — « X% ont débloqué » */}
          {rarity && (
            <p className="text-xs text-muted-foreground" role="status">
              {t("socialProof", { percent: rarity.unlock_percent })}
            </p>
          )}

          {/* Conditions d'obtention + barre de progression (verrouillé) — A-2 */}
          {!isEarned && (badge.criteria_text || progress) && (
            <div className="space-y-2 pt-2 border-t border-border/50">
              {badge.criteria_text && (
                <p className="text-sm text-primary font-medium">
                  {badge.criteria_text}
                  {progress && progress.target > 0 && (
                    <span className="text-foreground font-semibold ml-1">
                      — {progress.current} / {progress.target}
                    </span>
                  )}
                </p>
              )}
              {progress && progress.target > 0 && (
                <div
                  className="w-full bg-muted rounded-full h-2.5 overflow-hidden ring-1 ring-inset ring-border/50"
                  role="progressbar"
                  aria-valuenow={Math.round(progress.progress * 100)}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${badge.name}: ${Math.round(progress.progress * 100)}%`}
                >
                  <div
                    className="bg-primary h-2.5 rounded-full transition-all duration-500 min-w-[2px]"
                    style={{ width: `${Math.max(progress.progress * 100, 2)}%` }}
                  />
                </div>
              )}
            </div>
          )}

          <div className="flex items-center justify-between pt-3 border-t border-border/50 mt-auto">
            <div className="flex items-center gap-2 text-base font-semibold">
              <Trophy className="h-5 w-5 text-yellow-500" aria-hidden="true" />
              <span className="text-foreground">{badge.points_reward}</span>
              <span className="text-muted-foreground text-sm">pts</span>
            </div>

            {isEarned && userBadge?.earned_at && (
              <div className="text-xs text-muted-foreground bg-green-500/10 px-2 py-1 rounded">
                {t("earnedOn", {
                  date: new Date(userBadge.earned_at as string).toLocaleDateString(locale),
                })}
              </div>
            )}
          </div>
        </CardContent>

        {/* Effet de brillance pour les badges obtenus (désactivé si reduced motion) */}
        {isEarned && !shouldReduceMotion && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full animate-shimmer pointer-events-none" />
        )}
      </Card>
    </motion.div>
  );
}
