/**
 * Utilitaires d'export PDF pour les statistiques utilisateur
 */
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

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
 * Exporte les statistiques utilisateur en PDF
 */
export function exportStatsToPDF(stats: StatsData, username: string): void {
  const doc = new jsPDF();
  
  // Titre
  doc.setFontSize(18);
  doc.text('Statistiques Mathakine', 14, 22);
  
  // Informations utilisateur
  doc.setFontSize(12);
  doc.text(`Utilisateur: ${username}`, 14, 32);
  doc.text(`Date: ${new Date().toLocaleDateString('fr-FR')}`, 14, 38);
  
  // Tableau des statistiques
  autoTable(doc, {
    startY: 45,
    head: [['Métrique', 'Valeur']],
    body: [
      ['Exercices complétés', stats.total_exercises.toString()],
      ['Défis complétés', stats.total_challenges.toString()],
      ['Réponses correctes', stats.correct_answers.toString()],
      ['Réponses incorrectes', stats.incorrect_answers.toString()],
      ['Score moyen', `${stats.average_score.toFixed(1)}%`],
      ...(stats.level ? [['Niveau', stats.level.toString()]] : []),
      ...(stats.xp ? [['XP', stats.xp.toString()]] : []),
    ],
    theme: 'striped',
    headStyles: { fillColor: [99, 102, 241] },
  });
  
  // Sauvegarder le PDF
  doc.save(`mathakine-stats-${username}-${Date.now()}.pdf`);
}
