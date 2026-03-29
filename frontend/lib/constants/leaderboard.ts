/**
 * Constantes partagées pour le classement.
 * Utilisées dans leaderboard/page.tsx et LeaderboardWidget.tsx.
 */

export const RANK_MEDALS: Record<number, string> = {
  1: "🥇",
  2: "🥈",
  3: "🥉",
};

/** Icônes par bucket — clés canoniques API ``progression_rank`` / alias ``jedi_rank`` (F42-C3C, F43-A3). */
export const PROGRESSION_RANK_ICONS: Record<string, string> = {
  cadet: "🌟",
  scout: "🔭",
  explorer: "🧭",
  navigator: "🛰️",
  cartographer: "🗺️",
  commander: "⭐",
  stellar_archivist: "📚",
  cosmic_legend: "✨",
};

/** @deprecated Utiliser ``PROGRESSION_RANK_ICONS``. */
export const JEDI_RANK_ICONS = PROGRESSION_RANK_ICONS;

/** Couleurs du badge de rang (profil + leaderboard). */
export const PROGRESSION_RANK_TEXT_CLASS: Record<string, string> = {
  cadet: "text-slate-400",
  scout: "text-cyan-400",
  explorer: "text-blue-400",
  navigator: "text-sky-400",
  cartographer: "text-emerald-400",
  commander: "text-violet-400",
  stellar_archivist: "text-amber-400",
  cosmic_legend: "text-amber-300",
};

/** @deprecated Utiliser ``PROGRESSION_RANK_TEXT_CLASS``. */
export const JEDI_RANK_TEXT_CLASS = PROGRESSION_RANK_TEXT_CLASS;

/** Fond + contour discret pour le podium (rangs 1–3) — couleurs via tokens CSS par thème. */
export function leaderboardPodiumSurfaceClass(rank: number): string {
  switch (rank) {
    case 1:
      return "leaderboard-podium-surface--rank-1";
    case 2:
      return "leaderboard-podium-surface--rank-2";
    case 3:
      return "leaderboard-podium-surface--rank-3";
    default:
      return "leaderboard-podium-surface--rank-default";
  }
}
