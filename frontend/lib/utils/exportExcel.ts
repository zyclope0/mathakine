/**
 * Export Excel multi-feuilles (ExcelJS), data-driven, métadonnées workbook.
 */
import ExcelJS from "exceljs";
import { saveAs } from "file-saver";
import type { DashboardExportSnapshot } from "@/lib/dashboard/buildDashboardExportSnapshot";
import { buildDashboardExportFilenameBase } from "@/lib/dashboard/buildDashboardExportSnapshot";
import type { DashboardExportFormatLabels } from "@/lib/dashboard/exportFormatLabels";

const HEADER_FILL: ExcelJS.Fill = {
  type: "pattern",
  pattern: "solid",
  fgColor: { argb: "FF0F766E" },
};

function prettifyCategoryKey(key: string): string {
  return key.replace(/^exercises\.types\./i, "");
}

/** Valeur 0–1 pour format pourcentage Excel */
function toExcelPercentFraction(value: number | null): number | null {
  if (value === null || Number.isNaN(value)) return null;
  if (value >= 0 && value <= 1) return value;
  return value / 100;
}

function styleHeaderRow(row: ExcelJS.Row): void {
  row.font = { bold: true, color: { argb: "FFFFFFFF" } };
  row.fill = HEADER_FILL;
  row.alignment = { vertical: "middle" };
}

function freezeAndFilter(sheet: ExcelJS.Worksheet, colCount: number, headerRow = 1): void {
  sheet.views = [{ state: "frozen", ySplit: headerRow }];
  sheet.autoFilter = {
    from: { row: headerRow, column: 1 },
    to: { row: headerRow, column: colCount },
  };
}

function setColumnWidths(sheet: ExcelJS.Worksheet, widths: number[]): void {
  widths.forEach((w, i) => {
    sheet.getColumn(i + 1).width = w;
  });
}

function addSummarySheet(
  workbook: ExcelJS.Workbook,
  snapshot: DashboardExportSnapshot,
  labels: DashboardExportFormatLabels
): void {
  const s = snapshot.summary;
  const sheet = workbook.addWorksheet(labels.sheetSummary);
  const header = sheet.addRow([labels.columnMetric, labels.columnValue]);
  styleHeaderRow(header);

  type Kind = "percent" | "number" | "naNumber";

  const rows: { label: string; raw: number | null; kind: Kind }[] = [
    { label: labels.exercisesSolved, raw: s.total_exercises, kind: "number" },
    { label: labels.challengesCompletedLabel, raw: s.total_challenges, kind: "number" },
    { label: labels.successRate, raw: toExcelPercentFraction(s.success_rate), kind: "percent" },
    {
      label: labels.accountTotalPoints,
      raw: s.account_total_points,
      kind: s.account_total_points === null ? "naNumber" : "number",
    },
    {
      label: labels.accountXpInLevel,
      raw: s.account_xp_in_level,
      kind: s.account_xp_in_level === null ? "naNumber" : "number",
    },
  ];

  if (snapshot.gamification_level) {
    rows.push({
      label: labels.level,
      raw: snapshot.gamification_level.current,
      kind: "number",
    });
  }
  if (s.current_streak !== null) {
    rows.push({ label: labels.currentStreak, raw: s.current_streak, kind: "number" });
  }
  if (s.highest_streak !== null) {
    rows.push({ label: labels.highestStreak, raw: s.highest_streak, kind: "number" });
  }
  if (s.average_time_seconds !== null) {
    rows.push({ label: labels.averageTime, raw: s.average_time_seconds, kind: "number" });
  }
  rows.push({ label: labels.correctAnswers, raw: s.correct_answers, kind: "number" });
  rows.push({ label: labels.incorrectAnswers, raw: s.incorrect_answers, kind: "naNumber" });
  if (s.average_score !== null) {
    rows.push({
      label: labels.averageScoreSecondary,
      raw: toExcelPercentFraction(s.average_score),
      kind: "percent",
    });
  }

  rows.forEach((r) => {
    const row = sheet.addRow([r.label, r.raw]);
    const c = row.getCell(2);
    if (r.kind === "percent") {
      if (r.raw !== null) {
        c.value = r.raw;
        c.numFmt = "0.00%";
      } else {
        c.value = labels.notAvailable;
      }
    } else if (r.kind === "naNumber") {
      if (r.raw === null) {
        c.value = labels.notAvailable;
      } else {
        c.value = r.raw;
      }
    }
  });

  setColumnWidths(sheet, [44, 34]);
  freezeAndFilter(sheet, 2);
}

function addCategorySheet(
  workbook: ExcelJS.Workbook,
  snapshot: DashboardExportSnapshot,
  labels: DashboardExportFormatLabels
): void {
  const sheet = workbook.addWorksheet(labels.sheetPerformanceCategories);
  const header = sheet.addRow([
    labels.category,
    labels.completed,
    labels.accuracy,
    labels.attempts,
  ]);
  styleHeaderRow(header);

  const data = snapshot.performanceByCategory;
  if (data && Object.keys(data).length > 0) {
    Object.entries(data).forEach(([k, v]) => {
      const row = sheet.addRow([
        prettifyCategoryKey(k),
        v.completed,
        toExcelPercentFraction(v.accuracy),
        v.attempts ?? null,
      ]);
      row.getCell(3).numFmt = "0.00%";
      if (row.getCell(4).value === null) {
        row.getCell(4).value = labels.notAvailable;
      }
    });
  } else {
    sheet.addRow([labels.notAvailable, "", "", ""]);
  }
  setColumnWidths(sheet, [30, 14, 16, 16]);
  freezeAndFilter(sheet, 4);
}

function addPerformanceByTypeSheet(
  workbook: ExcelJS.Workbook,
  snapshot: DashboardExportSnapshot,
  labels: DashboardExportFormatLabels
): void {
  const sheet = workbook.addWorksheet(labels.sheetPerformanceTypes);
  const header = sheet.addRow([
    labels.exerciseType,
    labels.typeCompleted,
    labels.typeCorrect,
    labels.typeSuccessRate,
  ]);
  styleHeaderRow(header);

  const data = snapshot.performanceByType;
  if (data && Object.keys(data).length > 0) {
    Object.entries(data).forEach(([k, v]) => {
      const row = sheet.addRow([
        prettifyCategoryKey(k),
        v.completed,
        v.correct,
        toExcelPercentFraction(v.success_rate),
      ]);
      row.getCell(4).numFmt = "0.00%";
    });
  } else {
    sheet.addRow([labels.notAvailable, "", "", ""]);
  }
  setColumnWidths(sheet, [28, 14, 14, 16]);
  freezeAndFilter(sheet, 4);
}

function addLogicChallengesSheet(
  workbook: ExcelJS.Workbook,
  snapshot: DashboardExportSnapshot,
  labels: DashboardExportFormatLabels
): void {
  const sheet = workbook.addWorksheet(labels.sheetLogicChallenges);
  const cp = snapshot.challengesProgress;

  if (!cp) {
    const header = sheet.addRow([labels.columnMetric, labels.columnValue]);
    styleHeaderRow(header);
    sheet.addRow([labels.notAvailable, ""]);
    setColumnWidths(sheet, [40, 28]);
    freezeAndFilter(sheet, 2);
    return;
  }

  const summaryHeader = sheet.addRow([labels.columnMetric, labels.columnValue]);
  styleHeaderRow(summaryHeader);
  sheet.addRow([labels.logicCompletedTotal, `${cp.completed_challenges} / ${cp.total_challenges}`]);
  const rateFrac = toExcelPercentFraction(cp.success_rate);
  const sr = sheet.addRow([
    labels.logicSuccessRate,
    rateFrac !== null ? rateFrac : labels.notAvailable,
  ]);
  if (rateFrac !== null) {
    sr.getCell(2).numFmt = "0.00%";
  }
  sheet.addRow([labels.logicAverageTime, cp.average_time]);

  sheet.addRow([]);
  const detailHeader = sheet.addRow([
    labels.challengeTitle,
    labels.challengeCompleted,
    labels.challengeAttempts,
    labels.challengeBestTime,
  ]);
  styleHeaderRow(detailHeader);

  cp.challenges.forEach((c) => {
    sheet.addRow([
      c.title,
      c.is_completed ? labels.booleanYes : labels.booleanNo,
      c.attempts,
      c.best_time ?? labels.notAvailable,
    ]);
  });

  setColumnWidths(sheet, [38, 16, 12, 14]);
  freezeAndFilter(sheet, 4, detailHeader.number);
}

function addRecentActivitySheet(
  workbook: ExcelJS.Workbook,
  snapshot: DashboardExportSnapshot,
  labels: DashboardExportFormatLabels
): void {
  const sheet = workbook.addWorksheet(labels.sheetRecentActivity);
  const header = sheet.addRow([
    labels.activityType,
    labels.activityDescription,
    labels.activityTime,
    labels.activityCorrect,
  ]);
  styleHeaderRow(header);

  if (snapshot.recentActivity.length === 0) {
    sheet.addRow([labels.notAvailable, "", "", ""]);
  } else {
    snapshot.recentActivity.forEach((a) => {
      sheet.addRow([
        a.type,
        a.description,
        a.time,
        typeof a.is_correct === "boolean"
          ? a.is_correct
            ? labels.booleanYes
            : labels.booleanNo
          : "—",
      ]);
    });
  }
  setColumnWidths(sheet, [18, 44, 22, 12]);
  freezeAndFilter(sheet, 4);
}

function addDailyChallengesSheet(
  workbook: ExcelJS.Workbook,
  snapshot: DashboardExportSnapshot,
  labels: DashboardExportFormatLabels
): void {
  const sheet = workbook.addWorksheet(labels.sheetDailyChallenges);
  const header = sheet.addRow([
    labels.dailyType,
    labels.dailyTarget,
    labels.dailyCompleted,
    labels.dailyStatus,
    labels.dailyBonus,
    labels.dailyMetadata,
  ]);
  styleHeaderRow(header);

  if (snapshot.dailyChallenges.length === 0) {
    sheet.addRow([labels.notAvailable, "", "", "", "", ""]);
  } else {
    snapshot.dailyChallenges.forEach((d) => {
      sheet.addRow([
        d.challenge_type,
        d.target_count,
        d.completed_count,
        d.status,
        d.bonus_points,
        JSON.stringify(d.metadata ?? {}),
      ]);
    });
  }
  setColumnWidths(sheet, [22, 12, 12, 14, 10, 36]);
  freezeAndFilter(sheet, 6);
}

function addTimeSeriesSheet(
  workbook: ExcelJS.Workbook,
  snapshot: DashboardExportSnapshot,
  labels: DashboardExportFormatLabels
): void {
  const sheet = workbook.addWorksheet(labels.sheetTimeSeries);
  const byDay = snapshot.dailySeries;
  const timeline = snapshot.timeline;

  if (byDay?.labels?.length && byDay.datasets?.length) {
    const heads = [labels.seriesDate, ...byDay.datasets.map((d) => d.label || labels.seriesValue)];
    const header = sheet.addRow(heads);
    styleHeaderRow(header);
    const n = byDay.labels.length;
    for (let i = 0; i < n; i++) {
      const row: (string | number)[] = [byDay.labels[i] ?? ""];
      byDay.datasets.forEach((ds) => {
        row.push(ds.data[i] ?? 0);
      });
      sheet.addRow(row);
    }
    setColumnWidths(sheet, [16, ...byDay.datasets.map(() => 14)]);
    freezeAndFilter(sheet, heads.length);
    return;
  }

  if (timeline?.labels?.length && timeline.datasets?.length) {
    const heads = [
      labels.seriesDate,
      ...timeline.datasets.map((d) => d.label || labels.timelineDataset),
    ];
    const header = sheet.addRow(heads);
    styleHeaderRow(header);
    const n = timeline.labels.length;
    for (let i = 0; i < n; i++) {
      const row: (string | number)[] = [timeline.labels[i] ?? ""];
      timeline.datasets.forEach((ds) => {
        row.push(ds.data[i] ?? 0);
      });
      sheet.addRow(row);
    }
    setColumnWidths(sheet, [16, ...timeline.datasets.map(() => 14)]);
    freezeAndFilter(sheet, heads.length);
    return;
  }

  const header = sheet.addRow([labels.columnMetric, labels.columnValue]);
  styleHeaderRow(header);
  sheet.addRow([labels.notAvailable, ""]);
  setColumnWidths(sheet, [36, 28]);
  freezeAndFilter(sheet, 2);
}

/**
 * Exporte le snapshot dashboard en classeur Excel.
 */
export async function exportDashboardToExcel(
  snapshot: DashboardExportSnapshot,
  labels: DashboardExportFormatLabels
): Promise<void> {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = "Mathakine";
  workbook.lastModifiedBy = "Mathakine";
  workbook.created = new Date(snapshot.exportedAt);
  workbook.title = labels.workbookTitle;

  addSummarySheet(workbook, snapshot, labels);
  addCategorySheet(workbook, snapshot, labels);
  addPerformanceByTypeSheet(workbook, snapshot, labels);
  addLogicChallengesSheet(workbook, snapshot, labels);
  addRecentActivitySheet(workbook, snapshot, labels);
  addDailyChallengesSheet(workbook, snapshot, labels);
  addTimeSeriesSheet(workbook, snapshot, labels);

  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
  const base = buildDashboardExportFilenameBase(snapshot.username, snapshot.timeRangeSlug);
  saveAs(blob, `${base}.xlsx`);
}
