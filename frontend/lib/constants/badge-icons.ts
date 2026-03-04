/**
 * Icônes badges — SVG uniquement (s'adapte au thème via currentColor).
 * Priorité : SVG local → icon_url DB (http) → emoji catégorie.
 */

/** Mapping code API → nom fichier SVG (si différent) */
const CODE_TO_SVG: Record<string, string> = {
  premiers_pas: "first_steps",
  voie_du_padawan: "padawan_path",
  epreuve_du_chevalier: "knight_trial",
  maitre_des_additions: "addition_master",
  eclair_de_vitesse: "speed_demon",
  eclair_flash: "flash",
  journee_parfaite: "perfect_day",
  maitre_jedi: "jedi_master",
  grand_maitre: "grand_master",
  maitre_des_soustractions: "subtraction_master",
  maitre_des_multiplications: "multiplication_master",
  maitre_des_divisions: "division_master",
  explorateur: "explorer",
  explorateur_des_defis: "logic_explorer",
  maitre_des_enigmes: "logic_master",
  guerrier_polyvalent: "hybrid_warrior",
  polyvalent_total: "polyvalent_total",
  centurion: "centurion",
};

/** Résout le chemin SVG pour un code de badge. */
export function getBadgeIconPath(code: string | null | undefined): string | null {
  if (!code) return null;
  const normalized = code.toLowerCase().trim().replace(/\s+/g, "_");
  const svgName = CODE_TO_SVG[normalized] ?? normalized;
  return `/badges/svg/${svgName}.svg`;
}
