"use client";

import { useMemo } from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { FileText, FileSpreadsheet, Download, ChevronDown } from "lucide-react";
import { exportDashboardToPDF } from "@/lib/utils/exportPDF";
import { exportDashboardToExcel } from "@/lib/utils/exportExcel";
import type { DashboardExportSnapshot } from "@/lib/dashboard/buildDashboardExportSnapshot";
import type { DashboardExportFormatLabels } from "@/lib/dashboard/exportFormatLabels";
import { useAuth } from "@/hooks/useAuth";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { toast } from "sonner";
import { useTranslations } from "next-intl";

interface ExportButtonProps {
  snapshot: DashboardExportSnapshot | null;
}

function useDashboardExportFormatLabels(): DashboardExportFormatLabels {
  const t = useTranslations("dashboard.export.format");
  return useMemo(
    () => ({
      notAvailable: t("notAvailable"),
      scopeExcludedActions: t("scopeExcludedActions"),
      pdfTitle: t("pdfTitle"),
      period: t("period"),
      exportedAt: t("exportedAt"),
      lastDataUpdate: t("lastDataUpdate"),
      executiveSummary: t("executiveSummary"),
      successRate: t("successRate"),
      accountTotalPoints: t("accountTotalPoints"),
      accountXpInLevel: t("accountXpInLevel"),
      averageScoreSecondary: t("averageScoreSecondary"),
      incorrectAnswers: t("incorrectAnswers"),
      exercisesSolved: t("exercisesSolved"),
      challengesCompletedLabel: t("challengesCompletedLabel"),
      correctAnswers: t("correctAnswers"),
      level: t("level"),
      booleanYes: t("booleanYes"),
      booleanNo: t("booleanNo"),
      currentStreak: t("currentStreak"),
      highestStreak: t("highestStreak"),
      averageTime: t("averageTime"),
      performanceByCategory: t("performanceByCategory"),
      category: t("category"),
      completed: t("completed"),
      accuracy: t("accuracy"),
      attempts: t("attempts"),
      performanceByType: t("performanceByType"),
      exerciseType: t("exerciseType"),
      typeCompleted: t("typeCompleted"),
      typeCorrect: t("typeCorrect"),
      typeSuccessRate: t("typeSuccessRate"),
      logicChallengesSection: t("logicChallengesSection"),
      logicCompletedTotal: t("logicCompletedTotal"),
      logicSuccessRate: t("logicSuccessRate"),
      logicAverageTime: t("logicAverageTime"),
      challengeTitle: t("challengeTitle"),
      challengeCompleted: t("challengeCompleted"),
      challengeAttempts: t("challengeAttempts"),
      challengeBestTime: t("challengeBestTime"),
      recentActivity: t("recentActivity"),
      activityType: t("activityType"),
      activityDescription: t("activityDescription"),
      activityTime: t("activityTime"),
      activityCorrect: t("activityCorrect"),
      dailyChallengesSection: t("dailyChallengesSection"),
      dailyType: t("dailyType"),
      dailyTarget: t("dailyTarget"),
      dailyCompleted: t("dailyCompleted"),
      dailyStatus: t("dailyStatus"),
      dailyBonus: t("dailyBonus"),
      dailyMetadata: t("dailyMetadata"),
      statusPending: t("statusPending"),
      statusCompleted: t("statusCompleted"),
      statusExpired: t("statusExpired"),
      typeVolume: t("typeVolume"),
      typeSpecific: t("typeSpecific"),
      typeLogic: t("typeLogic"),
      seriesDate: t("seriesDate"),
      seriesValue: t("seriesValue"),
      timelineDataset: t("timelineDataset"),
      sheetSummary: t("sheetSummary"),
      sheetPerformanceCategories: t("sheetPerformanceCategories"),
      sheetPerformanceTypes: t("sheetPerformanceTypes"),
      sheetLogicChallenges: t("sheetLogicChallenges"),
      sheetRecentActivity: t("sheetRecentActivity"),
      sheetDailyChallenges: t("sheetDailyChallenges"),
      sheetTimeSeries: t("sheetTimeSeries"),
      columnMetric: t("columnMetric"),
      columnValue: t("columnValue"),
      workbookTitle: t("workbookTitle"),
    }),
    [t]
  );
}

export function ExportButton({ snapshot }: ExportButtonProps) {
  const { user } = useAuth();
  const { locale } = useLocaleStore();
  const t = useTranslations("dashboard.export");
  const formatLabels = useDashboardExportFormatLabels();

  const handleExportPDF = () => {
    if (!snapshot) {
      toast.error(t("noData"), {
        description: t("noDataDescription"),
      });
      return;
    }

    if (!user) {
      toast.error(t("noUser"), {
        description: t("noUserDescription"),
      });
      return;
    }

    try {
      exportDashboardToPDF(snapshot, formatLabels, { locale: locale ?? "fr" });
      toast.success(t("pdfSuccess"), {
        description: t("pdfSuccessDescription"),
      });
    } catch {
      toast.error(t("pdfError"), {
        description: t("pdfErrorDescription"),
      });
    }
  };

  const handleExportExcel = async () => {
    if (!snapshot) {
      toast.error(t("noData"), {
        description: t("noDataDescription"),
      });
      return;
    }

    if (!user) {
      toast.error(t("noUser"), {
        description: t("noUserDescription"),
      });
      return;
    }

    try {
      await exportDashboardToExcel(snapshot, formatLabels);
      toast.success(t("excelSuccess"), {
        description: t("excelSuccessDescription"),
      });
    } catch {
      toast.error(t("excelError"), {
        description: t("excelErrorDescription"),
      });
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          disabled={!snapshot}
          className="flex items-center gap-2"
          aria-label={t("exportLabel")}
        >
          <Download className="h-4 w-4" aria-hidden="true" />
          {t("export")}
          <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-44">
        <DropdownMenuItem
          onClick={handleExportPDF}
          className="flex items-center gap-2 cursor-pointer"
        >
          <FileText className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          {t("pdf")}
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={handleExportExcel}
          className="flex items-center gap-2 cursor-pointer"
        >
          <FileSpreadsheet className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          {t("excel")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
