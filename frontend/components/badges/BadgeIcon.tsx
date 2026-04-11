"use client";

import { useState } from "react";
import Image from "next/image";
import { getBadgeIconPath } from "@/lib/constants/badge-icons";
import { resolveNextImageRemoteDelivery } from "@/lib/utils/nextImageRemoteSource";
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

const REMOTE_PIXELS = { sm: 24, md: 32, lg: 40 } as const;

type BadgeIconSize = keyof typeof REMOTE_PIXELS;

function BadgeIconRemoteHttp({
  dbUrl,
  fallback,
  size,
  sizeClasses,
  containerClassName,
}: {
  dbUrl: string;
  fallback: string;
  size: BadgeIconSize;
  sizeClasses: Record<BadgeIconSize, string>;
  containerClassName: string;
}) {
  const [loadFailed, setLoadFailed] = useState(false);
  const delivery = resolveNextImageRemoteDelivery(dbUrl);
  const px = REMOTE_PIXELS[size];

  if (loadFailed) {
    return (
      <span className={containerClassName} aria-hidden="true">
        <span className="text-lg">{fallback}</span>
      </span>
    );
  }

  const sharedImgClass = cn("object-contain", sizeClasses[size]);
  const onError = () => setLoadFailed(true);

  const inner =
    delivery.mode === "next-image" ? (
      <Image
        src={delivery.src}
        alt=""
        width={px}
        height={px}
        className={sharedImgClass}
        sizes={`${px}px`}
        onError={onError}
      />
    ) : (
      // Intentional: host not in next.config `remotePatterns`; same as UserAvatar off-list URLs.
      // eslint-disable-next-line @next/next/no-img-element
      <img src={delivery.src} alt="" className={sharedImgClass} onError={onError} />
    );

  return (
    <span className={containerClassName} aria-hidden="true">
      {inner}
    </span>
  );
}

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

  const remoteContainerClass = cn(
    "shrink-0 flex items-center justify-center rounded-xl overflow-hidden",
    "bg-muted/30 ring-1 ring-border/40",
    containerSize[size],
    className
  );

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

  if (isHttp && dbUrl) {
    return (
      <BadgeIconRemoteHttp
        key={dbUrl}
        dbUrl={dbUrl}
        fallback={fallback}
        size={size}
        sizeClasses={sizeClasses}
        containerClassName={remoteContainerClass}
      />
    );
  }

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
