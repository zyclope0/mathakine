/**
 * Utilitaires d'export Excel pour les statistiques utilisateur
 */
import * as XLSX from 'xlsx';

export interface StatsData {
  total_exercises: number;
  total_challenges: number;
  correct_answers: number;
  incorrect_answers: number;
  average_score: number;
  level?: number;
  xp?: number;
}

/**
 * Exporte les statistiques utilisateur en Excel
 */
export function exportStatsToExcel(stats: StatsData, username: string): void {
  // Créer un workbook
  const workbook = XLSX.utils.book_new();
  
  // Créer les données
  const data = [
    ['Métrique', 'Valeur'],
    ['Exercices complétés', stats.total_exercises],
    ['Défis complétés', stats.total_challenges],
    ['Réponses correctes', stats.correct_answers],
    ['Réponses incorrectes', stats.incorrect_answers],
    ['Score moyen', `${stats.average_score.toFixed(1)}%`],
    ...(stats.level ? [['Niveau', stats.level]] : []),
    ...(stats.xp ? [['XP', stats.xp]] : []),
  ];
  
  // Créer une feuille de calcul
  const worksheet = XLSX.utils.aoa_to_sheet(data);
  
  // Ajouter la feuille au workbook
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Statistiques');
  
  // Sauvegarder le fichier
  XLSX.writeFile(workbook, `mathakine-stats-${username}-${Date.now()}.xlsx`);
}
