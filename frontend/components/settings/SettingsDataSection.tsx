"use client";

/**
 * Diagnostic, data export, account deletion (data tab).
 * FFI-L13 lot B.
 */

import { useTranslations } from "next-intl";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { BarChart2, Download, Trash2, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { DiagnosticStatusPayload } from "@/lib/settings/settingsPage";

export interface SettingsDataSectionProps {
  diagnosticStatus: DiagnosticStatusPayload | null;
  showDeleteConfirm: boolean;
  setShowDeleteConfirm: (value: boolean) => void;
  onNavigateToDiagnostic: () => void;
  onExportData: () => void;
  onDeleteAccount: () => void;
  isExportingData: boolean;
  isDeletingAccount: boolean;
}

export function SettingsDataSection({
  diagnosticStatus,
  showDeleteConfirm,
  setShowDeleteConfirm,
  onNavigateToDiagnostic,
  onExportData,
  onDeleteAccount,
  isExportingData,
  isDeletingAccount,
}: SettingsDataSectionProps) {
  const tDiagnostic = useTranslations("settings.diagnostic");
  const tData = useTranslations("settings.data");
  const tActions = useTranslations("settings.actions");

  return (
    <div className="space-y-8">
      <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
        <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
          <CardTitle className="flex items-center gap-2 text-xl">
            <BarChart2 className="h-5 w-5 text-primary" />
            {tDiagnostic("title")}
          </CardTitle>
          <CardDescription className="mt-1">{tDiagnostic("description")}</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
            <div className="flex flex-col gap-1 pr-4">
              <p className="text-sm font-medium text-foreground">
                {diagnosticStatus?.has_completed
                  ? tDiagnostic("lastDone", {
                      date: format(new Date(diagnosticStatus.latest!.completed_at), "dd/MM/yyyy", {
                        locale: fr,
                      }),
                    })
                  : tDiagnostic("notDone")}
              </p>
              {diagnosticStatus?.has_completed && diagnosticStatus.latest?.scores && (
                <p className="text-xs text-muted-foreground">
                  {tDiagnostic("scores", {
                    summary: Object.entries(diagnosticStatus.latest.scores)
                      .map(([type, s]) => `${type}: ${s.difficulty}`)
                      .join(" · "),
                  })}
                </p>
              )}
            </div>
            <Button
              size="sm"
              variant={diagnosticStatus?.has_completed ? "outline" : "default"}
              onClick={onNavigateToDiagnostic}
              className="shrink-0 mt-3 sm:mt-0"
            >
              {diagnosticStatus?.has_completed ? tDiagnostic("redo") : tDiagnostic("start")}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
        <CardContent className="p-0">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
            <div className="flex flex-col gap-1 pr-4">
              <p className="text-sm font-medium text-foreground">{tData("export")}</p>
              <p className="text-xs text-muted-foreground">{tData("exportDescription")}</p>
            </div>
            <Button
              onClick={onExportData}
              disabled={isExportingData}
              variant="outline"
              className="shrink-0 mt-3 sm:mt-0"
            >
              {isExportingData ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {tData("exporting")}
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  {tData("export")}
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-card/60 backdrop-blur-md border border-destructive/50 shadow-sm rounded-2xl p-6 md:p-8">
        <CardContent className="p-0">
          {showDeleteConfirm ? (
            <div className="space-y-4">
              <div className="py-4 border-b border-border/50">
                <p className="text-sm text-destructive font-medium">{tData("deleteWarning")}</p>
              </div>
              <div className="flex gap-2 pt-4">
                <Button
                  onClick={onDeleteAccount}
                  disabled={isDeletingAccount}
                  variant="destructive"
                  className="flex-1"
                >
                  {isDeletingAccount ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {tData("deleting")}
                    </>
                  ) : (
                    <>
                      <Trash2 className="mr-2 h-4 w-4" />
                      {tData("deleteConfirm")}
                    </>
                  )}
                </Button>
                <Button
                  onClick={() => setShowDeleteConfirm(false)}
                  variant="outline"
                  disabled={isDeletingAccount}
                >
                  {tActions("cancel")}
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
              <div className="flex flex-col gap-1 pr-4">
                <p className="text-sm font-medium text-foreground">{tData("delete")}</p>
                <p className="text-xs text-muted-foreground">{tData("deleteDescription")}</p>
              </div>
              <Button
                onClick={onDeleteAccount}
                variant="destructive"
                className="shrink-0 mt-3 sm:mt-0"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                {tData("delete")}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
