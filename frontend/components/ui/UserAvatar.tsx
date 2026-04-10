/**
 * Composant Avatar unifié.
 * Utilisé dans : leaderboard/page, LeaderboardWidget, et tout futur emplacement.
 * Fallback : initiale + dégradé déterministe si avatarUrl est absent.
 * Prêt pour l'ajout d'avatars uploadés (prop avatarUrl — cf. PLACEHOLDERS_ET_TODO.md § Avatars).
 */

import { cn } from "@/lib/utils";
import { getAvatarGradient } from "@/lib/utils/avatar";

const SIZE_CLASSES = {
  sm: "h-7 w-7 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-16 w-16 text-xl",
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

  if (avatarUrl) {
    return (
      // Intentional: avatar URLs are dynamic/external and this component does not know
      // intrinsic dimensions at build time; migrating to next/image needs a dedicated loader pass.
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={avatarUrl}
        alt={username}
        className={cn("flex-shrink-0 rounded-full object-cover select-none", sizeClass)}
      />
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
