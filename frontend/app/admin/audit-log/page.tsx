"use client";

import { useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAdminAuditLog } from "@/hooks/useAdminAuditLog";
import { ChevronLeft, ChevronRight, FileText } from "lucide-react";

const PAGE_SIZE = 30;

const ACTION_VALUES = [
  "all",
  "user_patch",
  "exercise_create",
  "exercise_update",
  "exercise_archive",
  "exercise_duplicate",
  "challenge_create",
  "challenge_update",
  "challenge_archive",
  "challenge_duplicate",
  "export_csv",
] as const;

const RESOURCE_VALUES = ["all", "user", "exercise", "challenge"] as const;

function localeTag(locale: string): string {
  return locale === "en" ? "en-US" : "fr-FR";
}

export default function AdminAuditLogPage() {
  const t = useTranslations("adminPages.auditLog");
  const locale = useLocale();
  const dateLocale = localeTag(locale);

  const [page, setPage] = useState(0);
  const [actionFilter, setActionFilter] = useState<string>("all");
  const [resourceFilter, setResourceFilter] = useState<string>("all");

  const { items, total, isLoading, error } = useAdminAuditLog({
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    ...(actionFilter !== "all" && { action: actionFilter }),
    ...(resourceFilter !== "all" && { resource_type: resourceFilter }),
  });

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;

  const actions = useMemo(
    () =>
      ACTION_VALUES.map((value) => ({
        value,
        label: t(`actions.${value}`),
      })),
    [t]
  );

  const resourceTypes = useMemo(
    () =>
      RESOURCE_VALUES.map((value) => ({
        value,
        label: t(`resourceTypes.${value}`),
      })),
    [t]
  );

  const actionLabelMap = useMemo(() => {
    const out: Record<string, string> = {};
    for (const v of ACTION_VALUES) {
      if (v !== "all") out[v] = t(`actions.${v}`);
    }
    return out;
  }, [t]);

  const auditActionLabel = (action: string) => actionLabelMap[action] ?? action;

  return (
    <div className="space-y-8">
      <PageHeader title={t("title")} description={t("description")} />

      <PageSection>
        <Card>
          <CardContent className="pt-6">
            <div className="mb-4 flex flex-wrap gap-3 items-end">
              <Select
                value={actionFilter}
                onValueChange={(v) => {
                  setActionFilter(v);
                  setPage(0);
                }}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder={t("actionPlaceholder")} />
                </SelectTrigger>
                <SelectContent>
                  {actions.map((a) => (
                    <SelectItem key={a.value} value={a.value}>
                      {a.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={resourceFilter}
                onValueChange={(v) => {
                  setResourceFilter(v);
                  setPage(0);
                }}
              >
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder={t("resourcePlaceholder")} />
                </SelectTrigger>
                <SelectContent>
                  {resourceTypes.map((r) => (
                    <SelectItem key={r.value} value={r.value}>
                      {r.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {error ? (
              <p className="py-8 text-center text-destructive">{t("errorLoading")}</p>
            ) : isLoading ? (
              <LoadingState message={t("loading")} />
            ) : items.length === 0 ? (
              <div className="py-12 text-center text-muted-foreground">
                <FileText className="mx-auto h-12 w-12 opacity-50 mb-2" />
                <p>{t("emptyTitle")}</p>
                <p className="text-sm mt-1">{t("emptyHint")}</p>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto rounded-md border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">{t("colDate")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colAdmin")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colAction")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colResource")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colDetails")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {items.map((log, idx) => (
                        <tr
                          key={log.id}
                          className={`border-b last:border-0 ${idx % 2 === 1 ? "bg-muted/30" : ""}`}
                        >
                          <td className="px-4 py-3 text-muted-foreground text-xs whitespace-nowrap">
                            {log.created_at
                              ? new Date(log.created_at).toLocaleString(dateLocale)
                              : "-"}
                          </td>
                          <td className="px-4 py-3">
                            {log.admin_username ??
                              (log.admin_user_id != null ? `#${log.admin_user_id}` : "-")}
                          </td>
                          <td className="px-4 py-3">{auditActionLabel(log.action)}</td>
                          <td className="px-4 py-3">
                            {log.resource_type}
                            {log.resource_id != null ? ` #${log.resource_id}` : ""}
                          </td>
                          <td className="px-4 py-3 text-muted-foreground text-xs max-w-[200px] truncate">
                            {log.details ? JSON.stringify(log.details) : "-"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {totalPages > 1 && (
                  <div className="mt-4 flex items-center justify-between">
                    <p className="text-sm text-muted-foreground">
                      {t("pagination", { total, current: page + 1, pages: totalPages })}
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.max(0, p - 1))}
                        disabled={page === 0}
                      >
                        <ChevronLeft className="h-4 w-4" />
                        {t("previous")}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                        disabled={page >= totalPages - 1}
                      >
                        {t("next")}
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </PageSection>
    </div>
  );
}
