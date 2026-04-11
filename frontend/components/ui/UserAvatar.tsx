/**
 * Composant Avatar unifié.
 * Utilisé dans : leaderboard/page, LeaderboardWidget, et tout futur emplacement.
 * Fallback : initiale + dégradé déterministe si avatarUrl est absent.
 * Prêt pour l'ajout d'avatars uploadés (prop avatarUrl — cf. PLACEHOLDERS_ET_TODO.md § Avatars).
 *
 * Images : `next/image` lorsque l'URL est autorisée par `remotePatterns` (voir
 * `resolveUserAvatarImageDelivery`) ; sinon `<img>` documenté pour les URL DB arbitraires.
 */

import Image from "next/image";
import { cn } from "@/lib/utils";
import { getAvatarGradient } from "@/lib/utils/avatar";
import { resolveUserAvatarImageDelivery } from "@/lib/utils/userAvatarImageSource";

const SIZE_CLASSES = {
  sm: "h-7 w-7 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-16 w-16 text-xl",
} as const;

/** Pixel width/height for `next/image` (matches Tailwind h-7 / h-10 / h-16 at default root). */
const AVATAR_PIXELS = {
  sm: 28,
  md: 40,
  lg: 64,
} as const;

interface UserAvatarProps {
  username: string;
  /** Taille du composant : sm (widget), md (liste), lg (profil) */
  size?: keyof typeof SIZE_CLASSES;
  /** URL d'un avatar uploadé. Si absent, fallback initiale + dégradé. */
  avatarUrl?: string | null;
}

export function UserAvatar({ username, size = "md", avatarUrl }: UserAvatarProps) {
  const gradient = getAvatarGradient(username);
  const sizeClass = SIZE_CLASSES[size];
  const pixelSize = AVATAR_PIXELS[size];
  const imageClassName = cn("flex-shrink-0 rounded-full object-cover select-none", sizeClass);

  if (avatarUrl) {
    const delivery = resolveUserAvatarImageDelivery(avatarUrl);
    if (delivery.mode === "next-image") {
      return (
        <Image
          src={delivery.src}
          alt={username}
          width={pixelSize}
          height={pixelSize}
          className={imageClassName}
          sizes={`${pixelSize}px`}
        />
      );
    }
    return (
      // Intentional: absolute URL not covered by next.config `images.remotePatterns` (arbitrary DB value).
      // eslint-disable-next-line @next/next/no-img-element
      <img src={delivery.src} alt={username} className={imageClassName} />
    );
  }

  return (
    <div
      className={cn(
        "flex-shrink-0 rounded-full flex items-center justify-center",
        "bg-gradient-to-br text-white font-bold select-none shadow-sm",
        sizeClass,
        gradient
      )}
      aria-hidden
    >
      {username.charAt(0).toUpperCase()}
    </div>
  );
}
