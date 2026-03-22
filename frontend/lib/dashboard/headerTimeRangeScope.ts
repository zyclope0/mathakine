/**
 * Dashboard header time range applies to {@link useUserStats} data (export, some charts).
 * It is not a global filter for every tab; hide the control where it would mislead users.
 */
export function shouldShowHeaderTimeRange(activeTab: string): boolean {
  // Le timeRange ne couvre que les agrégats issus de useUserStats (vue d'ensemble, export).
  // L'onglet « Mon Profil » mélange niveau global (hors période) et chiffres filtrés : pas de sélecteur global.
  return activeTab === "overview";
}
