/**
 * Constantes partagées pour le classement.
 * Utilisées dans leaderboard/page.tsx et LeaderboardWidget.tsx.
 */

export const RANK_MEDALS: Record<number, string> = {
  1: "🥇",
  2: "🥈",
  3: "🥉",
};

/** Icônes par bucket — clés canoniques API `progression_rank` (F42-C3C) ; `jedi_rank` = alias legacy même sémantique (F43-A3). */
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

/**
 * Couleurs du badge de rang — WCAG AA 4.5:1 sur fond clair (#f0f4ff S2).
 * Variantes *-600/*-700 utilisées pour garantir le contraste sur thème clair
 * et sur les thèmes sombres (les -600 restent lisibles sur fond sombre).
 */
export const PROGRESSION_RANK_TEXT_CLASS: Record<string, string> = {
  cadet: "text-slate-600",
  scout: "text-cyan-700",
  explorer: "text-blue-600",
  navigator: "text-sky-700",
  cartographer: "text-emerald-700",
  commander: "text-violet-600",
  stellar_archivist: "text-amber-600",
  cosmic_legend: "text-amber-500",
};

/** @deprecated Utiliser `PROGRESSION_RANK_TEXT_CLASS` — export conservé uniquement pour compat imports historiques. */
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
