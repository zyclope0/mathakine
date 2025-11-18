/**
 * Utilitaires d'export PDF pour les statistiques utilisateur
 */
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { UserStats } from '@/lib/validations/dashboard';

/**
 * Exporte les statistiques utilisateur en PDF
 */
export function exportStatsToPDF(stats: UserStats, username: string): void {
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
      ['Défis complétés', (stats.total_challenges || 0).toString()],
      ['Réponses correctes', stats.correct_answers.toString()],
      ['Réponses incorrectes', (stats.incorrect_answers || 0).toString()],
      ['Score moyen', stats.average_score ? `${stats.average_score.toFixed(1)}%` : '0%'],
      ...(stats.level && typeof stats.level === 'object' ? [['Niveau', stats.level.current.toString()]] : []),
      ...(stats.xp ? [['XP', stats.xp.toString()]] : []),
    ],
    theme: 'striped',
    headStyles: { fillColor: [99, 102, 241] },
  });
  
  // Sauvegarder le PDF
  doc.save(`mathakine-stats-${username}-${Date.now()}.pdf`);
}
