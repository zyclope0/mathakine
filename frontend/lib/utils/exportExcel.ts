/**
 * Utilitaires d'export Excel pour les statistiques utilisateur
 */
import * as XLSX from 'xlsx';
import type { UserStats } from '@/lib/validations/dashboard';

export interface ExportLabels {
  metric: string;
  value: string;
  exercisesCompleted: string;
  challengesCompleted: string;
  correctAnswers: string;
  incorrectAnswers: string;
  averageScore: string;
  level: string;
  xp: string;
  sheetName: string;
}

const defaultLabels: ExportLabels = {
  metric: 'Métrique',
  value: 'Valeur',
  exercisesCompleted: 'Exercices complétés',
  challengesCompleted: 'Défis complétés',
  correctAnswers: 'Réponses correctes',
  incorrectAnswers: 'Réponses incorrectes',
  averageScore: 'Score moyen',
  level: 'Niveau',
  xp: 'XP',
  sheetName: 'Statistiques',
};

/**
 * Exporte les statistiques utilisateur en Excel
 */
export function exportStatsToExcel(stats: UserStats, username: string, labels?: Partial<ExportLabels>): void {
  const l = { ...defaultLabels, ...labels };
  
  // Créer un workbook
  const workbook = XLSX.utils.book_new();
  
  // Créer les données
  const data = [
    [l.metric, l.value],
    [l.exercisesCompleted, stats.total_exercises],
    [l.challengesCompleted, stats.total_challenges || 0],
    [l.correctAnswers, stats.correct_answers],
    [l.incorrectAnswers, stats.incorrect_answers || 0],
    [l.averageScore, stats.average_score ? `${stats.average_score.toFixed(1)}%` : '0%'],
    ...(stats.level && typeof stats.level === 'object' ? [[l.level, stats.level.current]] : []),
    ...(stats.xp ? [[l.xp, stats.xp]] : []),
  ];
  
  // Créer une feuille de calcul
  const worksheet = XLSX.utils.aoa_to_sheet(data);
  
  // Ajouter la feuille au workbook
  XLSX.utils.book_append_sheet(workbook, worksheet, l.sheetName);
  
  // Sauvegarder le fichier
  XLSX.writeFile(workbook, `mathakine-stats-${username}-${Date.now()}.xlsx`);
}
