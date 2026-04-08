"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations, useLocale } from "next-intl";
import { Badge as BadgeComponent } from "@/components/ui/badge";
import { Trophy, Lock, CheckCircle, Heart } from "lucide-react";
import type { UserBadge } from "@/types/api";
import type { BadgeProgressSnapshot, BadgeWithCriteria, RarityInfo } from "@/lib/badges/types";
import {
  getDifficultyPresentationClasses,
  isRareRarityInfo,
  resolveCompactHighProgressMotivation,
  hasPresentationMedal,
  resolveIconGlowClass,
  resolveMedalSvgPath,
  shouldShowLockedMidMotivationLine,
  shouldShowLockedZeroMotivationLine,
} from "@/lib/badges/badgePresentation";
import { cn } from "@/lib/utils";
import { motion, type Variants, type Transition } from "framer-motion";
import { BadgeIcon } from "./BadgeIcon";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { readBadgeThematicTitleRaw } from "@/lib/gamification/badgeThematicTitle";

interface BadgeCardProps {
  badge: BadgeWithCriteria;
  userBadge?: UserBadge | null;
  isEarned: boolean;
  progress?: BadgeProgressSnapshot | null;
  index?: number;
  rarity?: RarityInfo | null;
  isPinned?: boolean;
  onTogglePin?: (badgeId: number) => void;
  canPin?: boolean;
  compact?: boolean;
}

function DifficultyMedal({
  difficulty,
  size = "sm",
}: {
  difficulty?: string | null | undefined;
  size?: "xs" | "sm";
}) {
  if (!hasPresentationMedal(difficulty)) return null;
  const src = resolveMedalSvgPath(difficulty);
  const cls = size === "xs" ? "h-4 w-4" : "h-3.5 w-3.5";
  return (
    /* eslint-disable-next-line @next/next/no-img-element */
    <img
      src={src}
      alt=""
      className={`${cls} object-contain inline-block shrink-0`}
      aria-hidden="true"
    />
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

  const difficultyColor = getDifficultyPresentationClasses(badge.difficulty);
  const thematicLine = readBadgeThematicTitleRaw(badge);

  const lockedHighMotivation =
    progress != null && progress.target > 0 && progress.progress >= 0.5
      ? resolveCompactHighProgressMotivation(
          progress.current,
          progress.target,
          progress.progress,
          progress.progress_detail
        )
      : null;

  const lockedMidMotivationVisible =
    progress != null &&
    shouldShowLockedMidMotivationLine(
      progress.current,
      progress.target,
      progress.progress,
      progress.progress_detail
    );

  const lockedZeroMotivationVisible =
    progress != null && shouldShowLockedZeroMotivationLine(progress.progress, progress.target);

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
          "card-spatial-depth badge-card-glass relative overflow-hidden transition-all duration-300 h-full flex flex-col",
          isEarned ? "cursor-pointer" : "opacity-60",
          isEarned && "badge-card-earned-compact group",
          badge.difficulty === "gold" && "shadow-lg shadow-yellow-500/10",
          badge.difficulty === "legendary" &&
            "ring-1 ring-amber-400/20 shadow-lg shadow-amber-400/15"
        )}
        role="article"
        aria-label={t("ariaLabel", {
          name: badge.name || t("noName"),
          status: isEarned ? t("earned") : t("locked"),
        })}
        tabIndex={isEarned ? 0 : undefined}
        title={isEarned ? t("expandHint") : undefined}
      >
        {/* Layout compact — flex-col centré, grande icône, glow */}
        {compact && isEarned ? (
          <CardHeader className="relative p-3 pt-4 flex flex-col items-center text-center gap-1.5">
            {/* Actions absolues en haut à droite */}
            <div className="absolute top-2 right-2 flex items-center gap-0.5">
              {canPin && onTogglePin && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    onTogglePin(badge.id);
                  }}
                  className={cn(
                    "p-1 rounded-full transition-all",
                    isPinned
                      ? "text-rose-400"
                      : "text-muted-foreground/50 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 hover:text-rose-400"
                  )}
                  aria-label={isPinned ? t("unpin") : t("pin")}
                  title={isPinned ? t("unpin") : t("pin")}
                >
                  <Heart
                    className={cn("h-3.5 w-3.5", isPinned && "fill-rose-400")}
                    aria-hidden="true"
                  />
                </button>
              )}
              <CheckCircle className="h-3.5 w-3.5 text-green-400 shrink-0" aria-hidden="true" />
            </div>

            {/* Icône centrale avec glow */}
            <div className="relative flex items-center justify-center mt-1">
              <div className={cn("badge-icon-glow", resolveIconGlowClass(badge.difficulty))} />
              <BadgeIcon
                code={badge.code}
                iconUrl={badge.icon_url}
                category={badge.category}
                difficulty={badge.difficulty}
                size="md"
                isEarned
              />
            </div>

            {/* Nom + pts centrés */}
            <p
              className="text-xs font-semibold leading-tight line-clamp-1 w-full px-1"
              title={badge.name || badge.code || ""}
            >
              {badge.name || badge.code || t("noName")}
            </p>
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground">
              <DifficultyMedal difficulty={badge.difficulty} size="xs" />
              <Trophy className="h-3 w-3 text-yellow-500 shrink-0" aria-hidden="true" />
              <span className="tabular-nums">{badge.points_reward} pts</span>
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
                  {!isEarned ? (
                    <div className="relative shrink-0">
                      <BadgeIcon
                        code={badge.code}
                        iconUrl={badge.icon_url}
                        category={badge.category}
                        difficulty={badge.difficulty}
                        size="md"
                        isEarned={false}
                      />
                      <div className="absolute inset-0 flex items-center justify-center rounded-xl bg-background/50">
                        <Lock className="h-4 w-4 text-muted-foreground/70" aria-hidden="true" />
                      </div>
                    </div>
                  ) : (
                    <BadgeIcon
                      code={badge.code}
                      iconUrl={badge.icon_url}
                      category={badge.category}
                      difficulty={badge.difficulty}
                      size="sm"
                      isEarned
                    />
                  )}
                  <span className="break-words">{badge.name || badge.code || t("noName")}</span>
                </CardTitle>
                {!isEarned && thematicLine && (
                  <CardDescription className="mt-2 text-primary-on-dark italic text-sm">
                    {thematicLine}
                  </CardDescription>
                )}
                {/* Compact: difficulté + pts toujours visibles */}
                {isEarned && (
                  <div className="mt-1.5 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                    <DifficultyMedal difficulty={badge.difficulty} size="sm" />
                    <span>
                      <Trophy
                        className="inline h-3.5 w-3.5 text-yellow-500 mr-0.5"
                        aria-hidden="true"
                      />
                      {badge.points_reward} pts
                    </span>
                  </div>
                )}
              </div>
              {/* Status — uniquement pour les badges obtenus (lock intégré dans l'icône) */}
              <div className="flex items-center gap-2 shrink-0 flex-wrap justify-end">
                {isEarned && (
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
                )}
                {!isEarned && isRareRarityInfo(rarity) && (
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
        )}{" "}
        {/* end of non-compact CardHeader branch */}
        <CardContent
          className={cn(
            "space-y-4",
            compact ? "flex-1 px-3 pb-0 pt-0" : "flex-1 flex flex-col min-h-0"
          )}
        >
          {/* Zone dépliable au survol (obtenus) : tout le détail */}
          {isEarned ? (
            <div className="badge-card-expandable space-y-4">
              {thematicLine && (
                <CardDescription className="text-primary-on-dark italic text-sm">
                  {thematicLine}
                </CardDescription>
              )}
              {isRareRarityInfo(rarity) && (
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
                    {t("noDescription")}
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
                    {t("noDescription")}
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
                      {progress.progress_detail?.type === "success_rate" ? (
                        <>
                          {" "}
                          —{" "}
                          {t("successRateDisplay", {
                            correct: progress.progress_detail.correct,
                            total: progress.progress_detail.total,
                            rate: progress.progress_detail.rate_pct,
                          })}
                        </>
                      ) : (
                        <>
                          {" "}
                          —{" "}
                          {t("progressLabel", {
                            current: progress.current,
                            target: progress.target,
                          })}
                        </>
                      )}
                    </span>
                  )}
                </p>
              )}
              {/* Label "encore X" :
                  - progress >= 0.5 → label motivant amber (chaud, proche)
                  - progress > 0 && < 0.5 → label neutre discret (commencé mais loin)
                  - progress === 0 && target > 0 → label informatif froid (jamais commencé)
                  Le backend fournit current/target pour TOUS les badges non débloqués
                  dès que la rule est calculable — pas besoin de données inventées. */}
              {lockedHighMotivation && (
                <p className="text-sm font-semibold text-amber-500/90" role="status">
                  {lockedHighMotivation.kind === "tuApproches" && t("tuApproches")}
                  {lockedHighMotivation.kind === "plusQueCorrect" &&
                    t("plusQueCorrect", { count: lockedHighMotivation.count })}
                  {lockedHighMotivation.kind === "plusQue" &&
                    t("plusQue", { count: lockedHighMotivation.count })}
                </p>
              )}
              {lockedMidMotivationVisible && progress && (
                <p className="text-xs text-muted-foreground" role="status">
                  {t("plusQue", { count: progress.target - progress.current })}
                </p>
              )}
              {lockedZeroMotivationVisible && progress && (
                <p className="text-xs text-muted-foreground" role="status">
                  {progress.progress_detail?.type === "success_rate"
                    ? t("successRateTarget", {
                        rate: progress.progress_detail.required_rate_pct,
                        min: progress.progress_detail.min_attempts,
                      })
                    : t("plusQue", { count: progress.target })}
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
              {/* Fallback pour badges dont la rule n'est pas calculable côté backend
                  (target = 0 ou null) — le seul cas où le frontend n'a vraiment pas de chiffre.
                  Les badges avec target > 0 (même à current=0) sont couverts par les labels ci-dessus. */}
              {!progress && badge.criteria_text && (
                <p className="text-xs text-muted-foreground/70 italic" role="status">
                  {t("noProgressYet")}
                </p>
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
