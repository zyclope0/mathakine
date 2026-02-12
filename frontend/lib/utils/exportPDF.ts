/**
 * Utilitaires d'export PDF pour les statistiques utilisateur
 */
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import type { UserStats } from "@/lib/validations/dashboard";

export interface PDFExportLabels {
  title: string;
  user: string;
  date: string;
  metric: string;
  value: string;
  exercisesCompleted: string;
  challengesCompleted: string;
  correctAnswers: string;
  incorrectAnswers: string;
  averageScore: string;
  level: string;
  xp: string;
}

const defaultLabels: PDFExportLabels = {
  title: "Statistiques Mathakine",
  user: "Utilisateur:",
  date: "Date:",
  metric: "Métrique",
  value: "Valeur",
  exercisesCompleted: "Exercices complétés",
  challengesCompleted: "Défis complétés",
  correctAnswers: "Réponses correctes",
  incorrectAnswers: "Réponses incorrectes",
  averageScore: "Score moyen",
  level: "Niveau",
  xp: "XP",
};

/**
 * Exporte les statistiques utilisateur en PDF
 */
export function exportStatsToPDF(
  stats: UserStats,
  username: string,
  labels?: Partial<PDFExportLabels>
): void {
  const l = { ...defaultLabels, ...labels };
  const doc = new jsPDF();

  // Titre
  doc.setFontSize(18);
  doc.text(l.title, 14, 22);

  // Informations utilisateur
  doc.setFontSize(12);
  doc.text(`${l.user} ${username}`, 14, 32);
  doc.text(`${l.date} ${new Date().toLocaleDateString("fr-FR")}`, 14, 38);

  // Tableau des statistiques
  autoTable(doc, {
    startY: 45,
    head: [[l.metric, l.value]],
    body: [
      [l.exercisesCompleted, stats.total_exercises.toString()],
      [l.challengesCompleted, (stats.total_challenges || 0).toString()],
      [l.correctAnswers, stats.correct_answers.toString()],
      [l.incorrectAnswers, (stats.incorrect_answers || 0).toString()],
      [l.averageScore, stats.average_score ? `${stats.average_score.toFixed(1)}%` : "0%"],
      ...(stats.level && typeof stats.level === "object"
        ? [[l.level, stats.level.current.toString()]]
        : []),
      ...(stats.xp ? [[l.xp, stats.xp.toString()]] : []),
    ],
    theme: "striped",
    headStyles: { fillColor: [99, 102, 241] },
  });

  // Sauvegarder le PDF
  doc.save(`mathakine-stats-${username}-${Date.now()}.pdf`);
}
