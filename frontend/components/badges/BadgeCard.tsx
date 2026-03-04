"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations, useLocale } from "next-intl";
import { Badge as BadgeComponent } from "@/components/ui/badge";
import { Trophy, Lock, CheckCircle, Heart } from "lucide-react";
import type { Badge, UserBadge } from "@/types/api";

type BadgeWithCriteria = Badge & { criteria_text?: string | null };
import { cn } from "@/lib/utils";
import { motion, type Variants, type Transition } from "framer-motion";
import { BadgeIcon } from "./BadgeIcon";
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
  badge: BadgeWithCriteria;
  userBadge?: UserBadge | null;
  isEarned: boolean;
  progress?: BadgeProgress | null;
  index?: number;
  rarity?: RarityInfo | null;
  isPinned?: boolean;
  onTogglePin?: (badgeId: number) => void;
  canPin?: boolean;
  compact?: boolean;
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

const MEDAL_SRCS: Record<string, string> = {
  bronze: "/badges/svg/medal-bronze.svg",
  silver: "/badges/svg/medal-silver.svg",
  gold: "/badges/svg/medal.svg",
  legendary: "/badges/svg/medal-diamond.svg",
};

function DifficultyMedal({ difficulty, size = "sm" }: { difficulty?: string | null | undefined; size?: "xs" | "sm" }) {
  if (!difficulty || !MEDAL_SRCS[difficulty]) return null;
  const cls = size === "xs" ? "h-4 w-4" : "h-3.5 w-3.5";
  return (
    /* eslint-disable-next-line @next/next/no-img-element */
    <img src={MEDAL_SRCS[difficulty]} alt="" className={`${cls} object-contain inline-block shrink-0`} aria-hidden="true" />
  );
}

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
  compact = false,
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

  const difficultyColor = getDifficultyColor(badge.difficulty);

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
      variants={variants as Variants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={transition as Transition}
      className="h-full"
    >
      <Card
        className={cn(
          "card-spatial-depth relative overflow-hidden transition-all duration-300 h-full flex flex-col",
          isEarned
            ? "border-primary/50 shadow-lg shadow-primary/20 hover:scale-[1.02] cursor-pointer"
            : "opacity-75 border-muted hover:opacity-90",
          isEarned && "badge-card-earned-compact group",
          // P3-12 : hiérarchie visuelle or/légendaire
          badge.difficulty === "gold" && "border-yellow-500/50 shadow-lg shadow-yellow-500/15",
          badge.difficulty === "legendary" &&
            "border-amber-400/60 ring-2 ring-amber-400/30 shadow-lg shadow-amber-400/20"
        )}
        role="article"
        aria-label={`Badge ${badge.name}${isEarned ? " obtenu" : " verrouillé"}`}
        tabIndex={isEarned ? 0 : undefined}
        title={isEarned ? t("expandHint") : undefined}
      >
        {/* Layout compact "list-item" pour cartes earned miniatures */}
        {compact && isEarned ? (
          <CardHeader className="p-3">
            <div className="flex items-center gap-2.5">
              {/* Icône badge */}
              <BadgeIcon
                code={badge.code}
                iconUrl={badge.icon_url}
                category={badge.category}
                difficulty={badge.difficulty}
                size="sm"
                isEarned
              />
              {/* Nom + pts — flex-1, nom tronqué sur 1 ligne */}
              <div className="flex-1 min-w-0">
                <p
                  className="text-sm font-semibold leading-tight truncate"
                  title={badge.name || badge.code || ""}
                >
                  {badge.name || badge.code || "Badge sans nom"}
                </p>
                <div className="flex items-center gap-1.5 mt-0.5 text-xs text-muted-foreground">
                  <DifficultyMedal difficulty={badge.difficulty} size="xs" />
                  <Trophy className="h-3 w-3 text-yellow-500 shrink-0" aria-hidden="true" />
                  <span className="tabular-nums">{badge.points_reward} pts</span>
                </div>
              </div>
              {/* Actions + check — centrés verticalement */}
              <div className="flex items-center gap-1 shrink-0">
                {canPin && onTogglePin && (
                  <button
                    type="button"
                    onClick={(e) => { e.preventDefault(); onTogglePin(badge.id); }}
                    className={cn(
                      "p-1 rounded-full transition-all",
                      isPinned
                        ? "bg-rose-500/20 text-rose-400 opacity-100"
                        : "text-muted-foreground hover:text-rose-400 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100"
                    )}
                    aria-label={isPinned ? t("unpin") : t("pin")}
                    title={isPinned ? t("unpin") : t("pin")}
                  >
                    <Heart className={cn("h-3.5 w-3.5", isPinned && "fill-rose-400")} aria-hidden="true" />
                  </button>
                )}
                <CheckCircle className="h-4 w-4 text-green-400 shrink-0" aria-hidden="true" />
              </div>
            </div>
          </CardHeader>
        ) : (
        <CardHeader className={cn("pb-4", isEarned && "pb-2")}>
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <CardTitle
                className={cn(
                  "flex items-center gap-2 font-bold",
                  isEarned ? "text-base md:text-lg" : "text-lg md:text-xl"
                )}
              >
                <BadgeIcon
                  code={badge.code}
                  iconUrl={badge.icon_url}
                  category={badge.category}
                  difficulty={badge.difficulty}
                  size={isEarned ? "sm" : "md"}
                  isEarned={isEarned}
                />
                <span className="break-words">{badge.name || badge.code || "Badge sans nom"}</span>
              </CardTitle>
              {!isEarned && badge.star_wars_title && (
                <CardDescription className="mt-2 text-primary-on-dark italic text-sm">
                  {badge.star_wars_title}
                </CardDescription>
              )}
              {/* Compact: difficulté + pts toujours visibles */}
              {isEarned && (
                <div className="mt-1.5 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                  <DifficultyMedal difficulty={badge.difficulty} size="sm" />
                  <span>
                    <Trophy className="inline h-3.5 w-3.5 text-yellow-500 mr-0.5" aria-hidden="true" />
                    {badge.points_reward} pts
                  </span>
                </div>
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
                        "p-1.5 rounded-full transition-all shrink-0",
                        isPinned
                          ? "bg-rose-500/20 text-rose-400 opacity-100"
                          : "text-muted-foreground hover:text-rose-400 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100"
                      )}
                      aria-label={isPinned ? t("unpin") : t("pin")}
                      title={isPinned ? t("unpin") : t("pin")}
                    >
                      <Heart
                        className={cn("h-4.5 w-4.5", isPinned && "fill-rose-400")}
                        aria-hidden="true"
                      />
                    </button>
                  )}
                  <CheckCircle className="h-5 w-5 text-green-400 shrink-0" aria-hidden="true" />
                </>
              ) : (
                <Lock
                  className="h-5 w-5 text-muted-foreground/60 shrink-0"
                  aria-label="Badge verrouillé"
                />
              )}
              {!isEarned && rarity && rarity.rarity === "rare" && (
                <BadgeComponent
                  variant="outline"
                  className="border-amber-500/50 bg-amber-500/20 text-amber-400 text-xs font-medium shrink-0"
                  aria-label={t("rarity.rare")}
                >
                  ✨ {t("rarity.rare")}
                </BadgeComponent>
              )}
              {!isEarned && (
                <BadgeComponent
                  variant="outline"
                  className={cn(
                    "badge-sweep shrink-0 text-sm inline-flex items-center gap-1",
                    difficultyColor.bg,
                    difficultyColor.text,
                    difficultyColor.border
                  )}
                  aria-label={`Difficulté: ${badge.difficulty}`}
                >
                  <DifficultyMedal difficulty={badge.difficulty} />
                </BadgeComponent>
              )}
            </div>
          </div>
        </CardHeader>
        )} {/* end of non-compact CardHeader branch */}

        <CardContent className={cn("space-y-4", compact ? "flex-1 px-3 pb-0 pt-0" : "flex-1 flex flex-col min-h-0")}>
          {/* Zone dépliable au survol (obtenus) : tout le détail */}
          {isEarned ? (
            <div className="badge-card-expandable space-y-4">
              {badge.star_wars_title && (
                <CardDescription className="text-primary-on-dark italic text-sm">
                  {badge.star_wars_title}
                </CardDescription>
              )}
              {rarity && rarity.rarity === "rare" && (
                <BadgeComponent
                  variant="outline"
                  className="border-amber-500/50 bg-amber-500/20 text-amber-400 text-xs font-medium shrink-0 w-fit"
                  aria-label={t("rarity.rare")}
                >
                  ✨ {t("rarity.rare")}
                </BadgeComponent>
              )}
              <div className="rounded-lg border border-border/40 bg-muted/30 px-3 py-2.5">
                {badge.description ? (
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {badge.description}
                  </p>
                ) : (
                  <p className="text-sm text-muted-foreground/60 italic leading-relaxed">
                    Description non disponible
                  </p>
                )}
              </div>
              {rarity && (
                <div
                  className="inline-flex w-fit rounded-full border border-border/50 bg-background/50 px-3 py-1 text-xs text-muted-foreground"
                  role="status"
                >
                  {t("socialProof", { percent: rarity.unlock_percent })}
                </div>
              )}
              <div className="flex items-center justify-between rounded-lg border border-border/40 bg-muted/20 px-3 py-2.5">
                <div className="flex items-center gap-2 text-base font-semibold">
                  <Trophy className="h-5 w-5 text-yellow-500" aria-hidden="true" />
                  <span className="text-foreground">{badge.points_reward}</span>
                  <span className="text-muted-foreground text-sm">pts</span>
                </div>
                {userBadge?.earned_at && (
                  <div className="text-xs text-muted-foreground bg-green-500/10 px-2 py-1 rounded-md">
                    {t("earnedOn", {
                      date: new Date(userBadge.earned_at as string).toLocaleDateString(locale),
                    })}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <>
              {/* Verrouillés: description + preuve sociale toujours visibles */}
              <div className="rounded-lg border border-border/40 bg-muted/30 px-3 py-2.5">
                {badge.description ? (
                  <p className="text-sm md:text-base text-muted-foreground leading-relaxed line-clamp-3">
                    {badge.description}
                  </p>
                ) : (
                  <p className="text-sm md:text-base text-muted-foreground/60 italic leading-relaxed line-clamp-3">
                    Description non disponible
                  </p>
                )}
              </div>
              {rarity && (
                <div
                  className="inline-flex w-fit rounded-full border border-border/50 bg-background/50 px-3 py-1 text-xs text-muted-foreground"
                  role="status"
                >
                  {t("socialProof", { percent: rarity.unlock_percent })}
                </div>
              )}
            </>
          )}

          {/* Conditions d'obtention + barre de progression (verrouillé) — A-2, B5 goal-gradient & loss aversion */}
          {!isEarned && (badge.criteria_text || progress) && (
            <div className="space-y-2 pt-2 border-t border-border/50">
              {badge.criteria_text && (
                <p className="text-sm font-medium">
                  <span className="text-foreground">{badge.criteria_text}</span>
                  {progress && progress.target > 0 && (
                    <span className="text-foreground font-semibold ml-1 tabular-nums">
                      — {progress.current} / {progress.target}
                    </span>
                  )}
                </p>
              )}
              {progress && progress.target > 0 && progress.progress >= 0.5 && (
                <p className="text-sm font-semibold text-amber-500/90" role="status">
                  {progress.target - progress.current > 0
                    ? t("plusQue", { count: progress.target - progress.current })
                    : t("tuApproches")}
                </p>
              )}
              {progress && progress.target > 0 && (
                <div
                  className="w-full bg-muted rounded-full h-3 overflow-hidden ring-1 ring-inset ring-border/60"
                  role="progressbar"
                  aria-valuenow={Math.round(progress.progress * 100)}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${badge.name}: ${Math.round(progress.progress * 100)}%`}
                >
                  <div
                    className="bg-primary h-3 rounded-full transition-all duration-500 min-w-[2px]"
                    style={{ width: `${Math.max(progress.progress * 100, 2)}%` }}
                  />
                </div>
              )}
            </div>
          )}

          {/* Footer — verrouillés uniquement (obtenus: footer dans zone dépliable) */}
          {!isEarned && (
            <div className="flex items-center justify-between pt-3 mt-auto rounded-lg border border-border/40 bg-muted/20 px-3 py-2.5">
              <div className="flex items-center gap-2 text-base font-semibold">
                <Trophy className="h-5 w-5 text-yellow-500" aria-hidden="true" />
                <span className="text-foreground">{badge.points_reward}</span>
                <span className="text-muted-foreground text-sm">pts</span>
              </div>
            </div>
          )}
        </CardContent>

        {/* Effet de brillance pour les badges obtenus (désactivé si reduced motion) */}
        {isEarned && !shouldReduceMotion && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full animate-shimmer pointer-events-none" />
        )}
      </Card>
    </motion.div>
  );
}
