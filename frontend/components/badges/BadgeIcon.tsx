"use client";

import { getBadgeIconPath } from "@/lib/constants/badge-icons";
import { cn } from "@/lib/utils";

const CATEGORY_EMOJI: Record<string, string> = {
  progression: "📈",
  mastery: "⭐",
  special: "✨",
};

function getCategoryFallback(category: string | null | undefined): string {
  return CATEGORY_EMOJI[category ?? ""] ?? "🏆";
}

type Difficulty = "bronze" | "silver" | "gold" | "legendary";

interface BadgeIconProps {
  code: string | null | undefined;
  iconUrl?: string | null | undefined;
  category?: string | null | undefined;
  difficulty?: Difficulty | string | null | undefined;
  size?: "sm" | "md" | "lg";
  isEarned?: boolean;
  className?: string;
}

/** Teintes du conteneur par difficulté — restent lisibles en dark/light */
const DIFFICULTY_CONTAINER: Record<Difficulty, { gradient: string; ring: string; icon: string }> = {
  bronze: {
    gradient: "from-orange-800/35 to-orange-700/15",
    ring: "ring-orange-700/50",
    icon: "text-orange-700 dark:text-orange-600",
  },
  silver: {
    gradient: "from-slate-400/30 to-slate-500/15",
    ring: "ring-slate-300/40",
    icon: "text-slate-400 dark:text-slate-300",
  },
  gold: {
    gradient: "from-yellow-400/30 to-yellow-300/15",
    ring: "ring-yellow-400/50",
    icon: "text-yellow-400 dark:text-yellow-300",
  },
  legendary: {
    gradient: "from-amber-400/25 to-amber-500/12",
    ring: "ring-amber-400/35",
    icon: "text-amber-400 dark:text-amber-300",
  },
};

/**
 * Icône de badge cohérente : SVG local (mask + currentColor) ou fallback.
 * S'adapte au thème sans fond blanc.
 */
export function BadgeIcon({
  code,
  iconUrl,
  category,
  difficulty,
  size = "md",
  isEarned = true,
  className,
}: BadgeIconProps) {
  const localPath = getBadgeIconPath(code);
  const dbUrl = iconUrl?.trim();
  const isHttp = dbUrl?.startsWith("http") ?? false;

  // Priorité : SVG local → URL DB → emoji
  const fallback = getCategoryFallback(category);

  const sizeClasses = {
    sm: "w-6 h-6",
    md: "w-8 h-8",
    lg: "w-10 h-10",
  };
  const containerSize = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12",
  };

  const difficultyKey = difficulty?.toLowerCase() as Difficulty | undefined;
  const diffStyles =
    isEarned && difficultyKey && difficultyKey in DIFFICULTY_CONTAINER
      ? DIFFICULTY_CONTAINER[difficultyKey as Difficulty]
      : null;

  // SVG local : masque CSS pour hériter de la couleur du thème
  if (localPath) {
    return (
      <span
        className={cn(
          "shrink-0 flex items-center justify-center rounded-xl transition-all duration-300",
          "ring-1",
          isEarned
            ? diffStyles
              ? `bg-gradient-to-br ${diffStyles.gradient} ${diffStyles.ring} ${diffStyles.icon}`
              : "bg-gradient-to-br from-primary/20 to-amber-500/10 ring-primary/30 text-primary"
            : "bg-muted/40 ring-border/40 text-muted-foreground/70",
          containerSize[size],
          className
        )}
        aria-hidden="true"
      >
        <span
          className={cn("block bg-current", sizeClasses[size])}
          style={{
            mask: `url(${localPath}) no-repeat center`,
            maskSize: "contain",
            WebkitMask: `url(${localPath}) no-repeat center`,
            WebkitMaskSize: "contain",
          }}
        />
      </span>
    );
  }

  // URL externe (DB)
  if (isHttp && dbUrl) {
    return (
      <span
        className={cn(
          "shrink-0 flex items-center justify-center rounded-xl overflow-hidden",
          "bg-muted/30 ring-1 ring-border/40",
          containerSize[size],
          className
        )}
        aria-hidden="true"
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={dbUrl}
          alt=""
          className={cn("object-contain", sizeClasses[size])}
          onError={(e) => {
            const el = e.currentTarget;
            el.style.display = "none";
            const parent = el.parentElement;
            if (parent) {
              const fallbackEl = document.createElement("span");
              fallbackEl.className = "text-lg";
              fallbackEl.textContent = fallback;
              parent.appendChild(fallbackEl);
            }
          }}
        />
      </span>
    );
  }

  // Emoji fallback
  return (
    <span
      className={cn(
        "shrink-0 flex items-center justify-center rounded-xl",
        "bg-muted/30 ring-1 ring-border/40",
        containerSize[size],
        className
      )}
      aria-hidden="true"
    >
      <span className="text-lg">{fallback}</span>
    </span>
  );
}
