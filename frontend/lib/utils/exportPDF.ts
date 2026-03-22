/**
 * Export PDF data-driven du dashboard (jsPDF + jspdf-autotable).
 * Thème teal cohérent avec l’UI actuelle (pas d’indigo legacy).
 */
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import type { DashboardExportSnapshot } from "@/lib/dashboard/buildDashboardExportSnapshot";
import {
  buildDashboardExportFilenameBase,
  sanitizeExportFilenameSegment,
} from "@/lib/dashboard/buildDashboardExportSnapshot";
import type { DashboardExportFormatLabels } from "@/lib/dashboard/exportFormatLabels";

const COL_PRIMARY: [number, number, number] = [15, 118, 110];
const COL_TEXT: [number, number, number] = [30, 41, 59];
const COL_MUTED: [number, number, number] = [100, 116, 139];

type JsPdfWithTable = jsPDF & { lastAutoTable?: { finalY: number } };

function finalY(doc: jsPDF): number {
  const d = doc as JsPdfWithTable;
  return d.lastAutoTable?.finalY ?? 40;
}

function prettifyCategoryKey(key: string): string {
  return key.replace(/^exercises\.types\./i, "");
}

function formatPercentDisplay(value: number | null, labels: DashboardExportFormatLabels): string {
  if (value === null || Number.isNaN(value)) {
    return labels.notAvailable;
  }
  const pct = value > 1 ? value : value * 100;
  return `${Math.round(pct)}%`;
}

function formatSeconds(value: number | null, labels: DashboardExportFormatLabels): string {
  if (value === null || Number.isNaN(value) || value < 0) {
    return labels.notAvailable;
  }
  if (value < 60) {
    return `${Math.round(value)}s`;
  }
  const m = Math.floor(value / 60);
  const s = Math.round(value % 60);
  return `${m}m ${s}s`;
}

function formatExportedDate(iso: string, locale: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString(locale === "en" ? "en-US" : "fr-FR", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

function formatActivityTime(time: string, locale: string): string {
  try {
    return new Date(time).toLocaleString(locale === "en" ? "en-US" : "fr-FR", {
      dateStyle: "short",
      timeStyle: "short",
    });
  } catch {
    return time;
  }
}

function dailyChallengeTypeLabel(type: string, labels: DashboardExportFormatLabels): string {
  if (type === "volume_exercises") return labels.typeVolume;
  if (type === "specific_type") return labels.typeSpecific;
  if (type === "logic_challenge") return labels.typeLogic;
  return type;
}

function dailyStatusLabel(status: string, labels: DashboardExportFormatLabels): string {
  if (status === "pending") return labels.statusPending;
  if (status === "completed") return labels.statusCompleted;
  if (status === "expired") return labels.statusExpired;
  return status;
}

/**
 * Exporte le snapshot dashboard en PDF structuré.
 */
export function exportDashboardToPDF(
  snapshot: DashboardExportSnapshot,
  labels: DashboardExportFormatLabels,
  options: { locale?: string } = {}
): void {
  const locale = options.locale ?? "fr";
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const pageW = doc.internal.pageSize.getWidth();
  const margin = 14;
  let y = 18;

  doc.setTextColor(...COL_TEXT);
  doc.setFontSize(18);
  doc.setFont("helvetica", "bold");
  doc.text(labels.pdfTitle, margin, y);
  y += 10;

  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...COL_MUTED);
  const safeUser = sanitizeExportFilenameSegment(snapshot.username);
  doc.text(`${safeUser}`, margin, y);
  y += 6;
  doc.text(`${labels.period}: ${snapshot.timeRangeLabel}`, margin, y);
  y += 6;
  doc.text(`${labels.exportedAt}: ${formatExportedDate(snapshot.exportedAt, locale)}`, margin, y);
  y += 6;
  if (snapshot.lastUpdated) {
    doc.text(
      `${labels.lastDataUpdate}: ${formatActivityTime(snapshot.lastUpdated, locale)}`,
      margin,
      y
    );
    y += 6;
  }
  doc.setFontSize(8);
  doc.text(labels.scopeExcludedActions, margin, y);
  y += 10;

  doc.setTextColor(...COL_TEXT);

  // — Résumé exécutif
  doc.setFontSize(13);
  doc.setFont("helvetica", "bold");
  doc.text(labels.executiveSummary, margin, y);
  y += 4;

  const s = snapshot.summary;
  const execBody: string[][] = [
    [labels.exercisesSolved, String(s.total_exercises)],
    [labels.challengesCompletedLabel, String(s.total_challenges)],
    [labels.successRate, formatPercentDisplay(s.success_rate, labels)],
    [
      labels.accountTotalPoints,
      s.account_total_points !== null ? String(s.account_total_points) : labels.notAvailable,
    ],
    [
      labels.accountXpInLevel,
      s.account_xp_in_level !== null ? String(s.account_xp_in_level) : labels.notAvailable,
    ],
  ];

  if (snapshot.gamification_level) {
    execBody.push([labels.level, String(snapshot.gamification_level.current)]);
  }
  if (s.current_streak !== null) {
    execBody.push([labels.currentStreak, String(s.current_streak)]);
  }
  if (s.highest_streak !== null) {
    execBody.push([labels.highestStreak, String(s.highest_streak)]);
  }
  if (s.average_time_seconds !== null) {
    execBody.push([labels.averageTime, formatSeconds(s.average_time_seconds, labels)]);
  }

  execBody.push([labels.correctAnswers, String(s.correct_answers)]);
  execBody.push([
    labels.incorrectAnswers,
    s.incorrect_answers !== null ? String(s.incorrect_answers) : labels.notAvailable,
  ]);

  if (s.average_score !== null) {
    execBody.push([labels.averageScoreSecondary, formatPercentDisplay(s.average_score, labels)]);
  }

  autoTable(doc, {
    startY: y,
    head: [[labels.columnMetric, labels.columnValue]],
    body: execBody,
    theme: "striped",
    headStyles: { fillColor: COL_PRIMARY, textColor: 255 },
    styles: { fontSize: 9, cellPadding: 2.5 },
    margin: { left: margin, right: margin },
  });
  y = finalY(doc) + 10;

  // — Performance par catégorie
  if (snapshot.performanceByCategory && Object.keys(snapshot.performanceByCategory).length > 0) {
    doc.setFontSize(13);
    doc.setFont("helvetica", "bold");
    doc.text(labels.performanceByCategory, margin, y);
    y += 4;

    const catRows = Object.entries(snapshot.performanceByCategory).map(([k, v]) => [
      prettifyCategoryKey(k),
      String(v.completed),
      formatPercentDisplay(v.accuracy, labels),
      v.attempts != null ? String(v.attempts) : labels.notAvailable,
    ]);

    autoTable(doc, {
      startY: y,
      head: [[labels.category, labels.completed, labels.accuracy, labels.attempts]],
      body: catRows,
      theme: "striped",
      headStyles: { fillColor: COL_PRIMARY, textColor: 255 },
      styles: { fontSize: 9 },
      margin: { left: margin, right: margin },
    });
    y = finalY(doc) + 10;
  }

  // — Performance par type (exercices)
  if (snapshot.performanceByType && Object.keys(snapshot.performanceByType).length > 0) {
    doc.setFontSize(13);
    doc.setFont("helvetica", "bold");
    doc.text(labels.performanceByType, margin, y);
    y += 4;

    const typeRows = Object.entries(snapshot.performanceByType).map(([k, v]) => [
      prettifyCategoryKey(k),
      String(v.completed),
      String(v.correct),
      formatPercentDisplay(v.success_rate, labels),
    ]);

    autoTable(doc, {
      startY: y,
      head: [
        [labels.exerciseType, labels.typeCompleted, labels.typeCorrect, labels.typeSuccessRate],
      ],
      body: typeRows,
      theme: "striped",
      headStyles: { fillColor: COL_PRIMARY, textColor: 255 },
      styles: { fontSize: 9 },
      margin: { left: margin, right: margin },
    });
    y = finalY(doc) + 10;
  }

  // — Défis logiques
  if (snapshot.challengesProgress) {
    const cp = snapshot.challengesProgress;
    doc.setFontSize(13);
    doc.setFont("helvetica", "bold");
    doc.text(labels.logicChallengesSection, margin, y);
    y += 4;

    const summaryRows: string[][] = [
      [labels.logicCompletedTotal, `${cp.completed_challenges} / ${cp.total_challenges}`],
      [labels.logicSuccessRate, formatPercentDisplay(cp.success_rate, labels)],
      [labels.logicAverageTime, formatSeconds(cp.average_time, labels)],
    ];

    autoTable(doc, {
      startY: y,
      head: [[labels.columnMetric, labels.columnValue]],
      body: summaryRows,
      theme: "striped",
      headStyles: { fillColor: COL_PRIMARY, textColor: 255 },
      styles: { fontSize: 9 },
      margin: { left: margin, right: margin },
    });
    y = finalY(doc) + 6;

    if (cp.challenges.length > 0) {
      const detail = cp.challenges
        .slice(0, 40)
        .map((c) => [
          c.title,
          c.is_completed ? labels.booleanYes : labels.booleanNo,
          String(c.attempts),
          c.best_time != null ? formatSeconds(c.best_time, labels) : labels.notAvailable,
        ]);

      autoTable(doc, {
        startY: y,
        head: [
          [
            labels.challengeTitle,
            labels.challengeCompleted,
            labels.challengeAttempts,
            labels.challengeBestTime,
          ],
        ],
        body: detail,
        theme: "striped",
        headStyles: { fillColor: COL_PRIMARY, textColor: 255 },
        styles: { fontSize: 8 },
        margin: { left: margin, right: margin },
      });
      y = finalY(doc) + 10;
    }
  }

  // — Activité récente
  if (snapshot.recentActivity.length > 0) {
    doc.setFontSize(13);
    doc.setFont("helvetica", "bold");
    doc.text(labels.recentActivity, margin, y);
    y += 4;

    const rows = snapshot.recentActivity
      .slice(0, 35)
      .map((a) => [
        a.type,
        a.description,
        formatActivityTime(a.time, locale),
        typeof a.is_correct === "boolean"
          ? a.is_correct
            ? labels.booleanYes
            : labels.booleanNo
          : "—",
      ]);

    autoTable(doc, {
      startY: y,
      head: [
        [
          labels.activityType,
          labels.activityDescription,
          labels.activityTime,
          labels.activityCorrect,
        ],
      ],
      body: rows,
      theme: "striped",
      headStyles: { fillColor: COL_PRIMARY, textColor: 255 },
      styles: { fontSize: 8 },
      margin: { left: margin, right: margin },
    });
    y = finalY(doc) + 10;
  }

  // — Défis du jour
  if (snapshot.dailyChallenges.length > 0) {
    doc.setFontSize(13);
    doc.setFont("helvetica", "bold");
    doc.text(labels.dailyChallengesSection, margin, y);
    y += 4;

    const dailyRows = snapshot.dailyChallenges.map((d) => [
      dailyChallengeTypeLabel(d.challenge_type, labels),
      String(d.target_count),
      String(d.completed_count),
      dailyStatusLabel(d.status, labels),
      String(d.bonus_points),
      JSON.stringify(d.metadata ?? {}),
    ]);

    autoTable(doc, {
      startY: y,
      head: [
        [
          labels.dailyType,
          labels.dailyTarget,
          labels.dailyCompleted,
          labels.dailyStatus,
          labels.dailyBonus,
          labels.dailyMetadata,
        ],
      ],
      body: dailyRows,
      theme: "striped",
      headStyles: { fillColor: COL_PRIMARY, textColor: 255 },
      styles: { fontSize: 8 },
      margin: { left: margin, right: margin },
    });
    y = finalY(doc) + 10;
  }

  // Footer toutes pages
  const foot = `Mathakine · ${safeUser} · ${snapshot.timeRangeLabel}`;
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    const h = doc.internal.pageSize.getHeight();
    doc.setFontSize(8);
    doc.setTextColor(...COL_MUTED);
    doc.text(foot, margin, h - 8);
    doc.text(`${i} / ${pageCount}`, pageW - margin - 12, h - 8);
  }

  const base = buildDashboardExportFilenameBase(snapshot.username, snapshot.timeRangeSlug);
  doc.save(`${base}.pdf`);
}
