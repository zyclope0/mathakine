/**
 * Constantes partagées pour le classement.
 * Utilisées dans leaderboard/page.tsx et LeaderboardWidget.tsx.
 */

export const RANK_MEDALS: Record<number, string> = {
  1: "🥇",
  2: "🥈",
  3: "🥉",
};

export const JEDI_RANK_ICONS: Record<string, string> = {
  youngling: "🌟",
  padawan: "⚔️",
  knight: "🗡️",
  master: "👑",
  grand_master: "✨",
};

/** Couleur du libellé / icône de rang Jedi (cohérent profil + leaderboard). */
export const JEDI_RANK_TEXT_CLASS: Record<string, string> = {
  youngling: "text-slate-400",
  padawan: "text-blue-400",
  knight: "text-green-400",
  master: "text-purple-400",
  grand_master: "text-amber-400",
};

/** Fond + contour discret pour le podium (rangs 1–3). */
export function leaderboardPodiumSurfaceClass(rank: number): string {
  switch (rank) {
    case 1:
      return "bg-amber-500/10 ring-1 ring-inset ring-amber-500/25";
    case 2:
      return "bg-slate-500/10 ring-1 ring-inset ring-slate-400/25";
    case 3:
      return "bg-amber-700/10 ring-1 ring-inset ring-amber-700/25";
    default:
      return "bg-muted/25";
  }
}
