/**
 * Utilitaires Avatar — gradient déterministe basé sur le pseudo.
 * Source unique pour leaderboard/page.tsx, LeaderboardWidget et tout futur composant.
 */

export const AVATAR_GRADIENTS = [
  "from-violet-500 to-purple-700",
  "from-blue-500 to-cyan-600",
  "from-emerald-500 to-teal-600",
  "from-orange-500 to-amber-600",
  "from-rose-500 to-pink-600",
  "from-indigo-500 to-blue-600",
  "from-fuchsia-500 to-violet-600",
  "from-sky-500 to-blue-600",
] as const;

/**
 * Retourne un gradient Tailwind déterministe basé sur le hash du nom d'utilisateur.
 * Même username → même couleur, stable entre les rendus.
 */
export function getAvatarGradient(username: string): string {
  let hash = 0;
  for (let i = 0; i < username.length; i++) {
    hash = (hash * 31 + username.charCodeAt(i)) % AVATAR_GRADIENTS.length;
  }
  return AVATAR_GRADIENTS[Math.abs(hash)] ?? "from-violet-500 to-purple-700";
}
