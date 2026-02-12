/**
 * Utilitaires d'export Excel pour les statistiques utilisateur
 */
import ExcelJS from "exceljs";
import { saveAs } from "file-saver";
import type { UserStats } from "@/lib/validations/dashboard";

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
  metric: "Métrique",
  value: "Valeur",
  exercisesCompleted: "Exercices complétés",
  challengesCompleted: "Défis complétés",
  correctAnswers: "Réponses correctes",
  incorrectAnswers: "Réponses incorrectes",
  averageScore: "Score moyen",
  level: "Niveau",
  xp: "XP",
  sheetName: "Statistiques",
};

/**
 * Exporte les statistiques utilisateur en Excel
 */
export async function exportStatsToExcel(
  stats: UserStats,
  username: string,
  labels?: Partial<ExportLabels>
): Promise<void> {
  const l = { ...defaultLabels, ...labels };

  // Créer un workbook
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet(l.sheetName);

  // En-tête
  worksheet.addRow([l.metric, l.value]);

  // Style de l'en-tête
  const headerRow = worksheet.getRow(1);
  headerRow.font = { bold: true };
  headerRow.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FF6366F1" } };
  headerRow.font = { bold: true, color: { argb: "FFFFFFFF" } };

  // Données
  worksheet.addRow([l.exercisesCompleted, stats.total_exercises]);
  worksheet.addRow([l.challengesCompleted, stats.total_challenges || 0]);
  worksheet.addRow([l.correctAnswers, stats.correct_answers]);
  worksheet.addRow([l.incorrectAnswers, stats.incorrect_answers || 0]);
  worksheet.addRow([
    l.averageScore,
    stats.average_score ? `${stats.average_score.toFixed(1)}%` : "0%",
  ]);

  if (stats.level && typeof stats.level === "object") {
    worksheet.addRow([l.level, stats.level.current]);
  }
  if (stats.xp) {
    worksheet.addRow([l.xp, stats.xp]);
  }

  // Ajuster la largeur des colonnes
  worksheet.columns.forEach((column) => {
    column.width = 25;
  });

  // Générer et télécharger le fichier
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
  saveAs(blob, `mathakine-stats-${username}-${Date.now()}.xlsx`);
}
