"use client";

import { useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getUserRoleLabel } from "@/lib/auth/userRoles";
import {
  type FeedbackReportItem,
  type FeedbackStatus,
  useAdminFeedback,
} from "@/hooks/useAdminFeedback";
import { MessageCircle, FileQuestion, AlertTriangle, Bug, ExternalLink, Copy } from "lucide-react";
import { toast } from "sonner";

const TYPE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  exercise: FileQuestion,
  challenge: AlertTriangle,
  ui: Bug,
  other: MessageCircle,
};

function localeTag(locale: string): string {
  return locale === "en" ? "en-US" : "fr-FR";
}

function FeedbackStatusBadge({
  status,
  labels,
}: {
  status: FeedbackStatus;
  labels: Record<FeedbackStatus, string>;
}) {
  const label = labels[status];
  if (status === "new") {
    return (
      <Badge variant="outline" className="border-primary/40 text-primary">
        {label}
      </Badge>
    );
  }
  if (status === "read") {
    return <Badge variant="secondary">{label}</Badge>;
  }
  return (
    <Badge
      variant="outline"
      className="border-emerald-600/35 bg-emerald-50 text-emerald-900 dark:border-emerald-500/35 dark:bg-emerald-950/50 dark:text-emerald-100"
    >
      {label}
    </Badge>
  );
}

function feedbackDebugBadges(item: FeedbackReportItem) {
  return (
    <div className="flex flex-wrap gap-1 text-xs text-muted-foreground">
      {item.user_role && (
        <span className="rounded bg-muted px-1.5 py-0.5">{getUserRoleLabel(item.user_role)}</span>
      )}
      {item.active_theme && (
        <span className="rounded bg-muted px-1.5 py-0.5">{item.active_theme}</span>
      )}
      {item.ni_state === "on" && (
        <span className="rounded bg-amber-100 px-1.5 py-0.5 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
          NI:on
        </span>
      )}
      {item.component_id && item.component_id !== "FeedbackFab" && (
        <span className="rounded bg-muted px-1.5 py-0.5 font-mono">{item.component_id}</span>
      )}
      {!item.user_role &&
        !item.active_theme &&
        item.ni_state !== "on" &&
        (!item.component_id || item.component_id === "FeedbackFab") && (
          <span className="text-muted-foreground">—</span>
        )}
    </div>
  );
}

export default function AdminFeedbackPage() {
  const t = useTranslations("adminPages.feedback");
  const locale = useLocale();
  const dateLocale = localeTag(locale);
  const {
    feedback,
    isLoading,
    error,
    updateFeedbackStatus,
    isUpdatingStatus,
    deleteFeedback,
    isDeletingFeedback,
  } = useAdminFeedback();
  const [selectedItem, setSelectedItem] = useState<FeedbackReportItem | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  const typeLabels = useMemo(
    () => ({
      exercise: t("types.exercise"),
      challenge: t("types.challenge"),
      ui: t("types.ui"),
      other: t("types.other"),
    }),
    [t]
  );

  const statusLabels = useMemo(
    () =>
      ({
        new: t("statusNew"),
        read: t("statusRead"),
        resolved: t("statusResolved"),
      }) satisfies Record<FeedbackStatus, string>,
    [t]
  );

  const formatItemDate = (item: FeedbackReportItem) =>
    item.created_at ? new Date(item.created_at).toLocaleString(dateLocale) : "—";

  const typeLabelFor = (item: FeedbackReportItem) =>
    typeLabels[item.feedback_type as keyof typeof typeLabels] ?? item.feedback_type;

  const buildPlainTextForCopy = (item: FeedbackReportItem): string => {
    const typeL = typeLabelFor(item);
    const dateStr = formatItemDate(item);
    const lines: string[] = [];
    lines.push(t("detailTitle", { type: typeL, date: dateStr }));
    lines.push(`${t("detailUser")}: ${item.username ?? "—"}`);
    lines.push("");
    lines.push(t("detailContext"));
    if (item.exercise_id) {
      lines.push(`- ${t("linkExercise", { id: item.exercise_id })}`);
    }
    if (item.challenge_id) {
      lines.push(`- ${t("linkChallenge", { id: item.challenge_id })}`);
    }
    if (item.page_url) {
      lines.push(`- ${t("detailPage")}: ${item.page_url}`);
    }
    if (!item.exercise_id && !item.challenge_id && !item.page_url) {
      lines.push("—");
    }
    lines.push("");
    lines.push(t("detailDebug"));
    const debugParts: string[] = [];
    if (item.user_role) {
      debugParts.push(getUserRoleLabel(item.user_role));
    }
    if (item.active_theme) {
      debugParts.push(item.active_theme);
    }
    if (item.ni_state === "on") {
      debugParts.push("NI:on");
    }
    if (item.component_id && item.component_id !== "FeedbackFab") {
      debugParts.push(item.component_id);
    }
    lines.push(debugParts.length > 0 ? debugParts.join(", ") : "—");
    lines.push("");
    lines.push(t("detailDescriptionLabel"));
    lines.push(item.description?.trim() ? item.description : "—");
    return lines.join("\n");
  };

  const handleCopyDetails = async () => {
    if (!selectedItem) {
      return;
    }
    try {
      await navigator.clipboard.writeText(buildPlainTextForCopy(selectedItem));
      toast.success(t("copySuccess"));
    } catch {
      /* Clipboard API refused or unavailable */
    }
  };

  const handleStatusUpdate = async (next: FeedbackStatus) => {
    if (!selectedItem) {
      return;
    }
    try {
      await updateFeedbackStatus({ feedbackId: selectedItem.id, status: next });
      toast.success(t("statusUpdateSuccess"));
      setSelectedItem((prev) => (prev ? { ...prev, status: next } : null));
    } catch {
      toast.error(t("statusUpdateError"));
    }
  };

  const handleConfirmDelete = async () => {
    if (!selectedItem) {
      return;
    }
    const id = selectedItem.id;
    try {
      await deleteFeedback(id);
      toast.success(t("deleteSuccess"));
      setDeleteConfirmOpen(false);
      setSelectedItem(null);
    } catch {
      toast.error(t("deleteError"));
    }
  };

  return (
    <div className="space-y-8">
      <PageHeader title={t("title")} description={t("description")} />

      <PageSection>
        <Card>
          <CardContent className="pt-6">
            {error ? (
              <p className="py-8 text-center text-destructive">{t("errorLoading")}</p>
            ) : isLoading ? (
              <LoadingState message={t("loading")} />
            ) : feedback.length === 0 ? (
              <div className="rounded-md border border-dashed p-12 text-center text-muted-foreground">
                <MessageCircle className="mx-auto mb-3 h-12 w-12 opacity-50" />
                <p>{t("emptyTitle")}</p>
                <p className="mt-1 text-sm">{t("emptyHint")}</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left font-medium">{t("colDate")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colType")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colStatus")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colUser")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colContext")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colDescription")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colPage")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colDebug")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {feedback.map((item) => {
                      const Icon = TYPE_ICONS[item.feedback_type] ?? MessageCircle;
                      const descTrimmed = item.description?.trim();
                      return (
                        <tr key={item.id} className="border-b last:border-0 hover:bg-muted/50">
                          <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">
                            {item.created_at
                              ? new Date(item.created_at).toLocaleString(dateLocale)
                              : "-"}
                          </td>
                          <td className="px-4 py-3">
                            <Badge variant="outline" className="flex w-fit items-center gap-1">
                              <Icon className="h-3 w-3" />
                              {typeLabels[item.feedback_type as keyof typeof typeLabels] ??
                                item.feedback_type}
                            </Badge>
                          </td>
                          <td className="px-4 py-3">
                            <FeedbackStatusBadge status={item.status} labels={statusLabels} />
                          </td>
                          <td className="px-4 py-3">
                            {item.username ?? <span className="text-muted-foreground">—</span>}
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex flex-wrap gap-1">
                              {item.exercise_id && (
                                <Button variant="ghost" size="sm" asChild className="h-7 text-xs">
                                  <Link href={`/exercises/${item.exercise_id}`}>
                                    {t("linkExercise", { id: item.exercise_id })}
                                  </Link>
                                </Button>
                              )}
                              {item.challenge_id && (
                                <Button variant="ghost" size="sm" asChild className="h-7 text-xs">
                                  <Link href={`/challenge/${item.challenge_id}`}>
                                    {t("linkChallenge", { id: item.challenge_id })}
                                  </Link>
                                </Button>
                              )}
                              {!item.exercise_id && !item.challenge_id && (
                                <span className="text-muted-foreground">—</span>
                              )}
                            </div>
                          </td>
                          <td className="max-w-[280px] px-4 py-3">
                            <div className="flex flex-col gap-1.5">
                              <span className="line-clamp-2">
                                {item.description || (
                                  <span className="text-muted-foreground">—</span>
                                )}
                              </span>
                              {descTrimmed ? (
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  className="h-7 w-fit shrink-0 px-2 text-xs"
                                  onClick={() => setSelectedItem(item)}
                                >
                                  {t("viewDetails")}
                                </Button>
                              ) : null}
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            {item.page_url ? (
                              <a
                                href={item.page_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-primary hover:underline"
                              >
                                <ExternalLink className="h-3 w-3" />
                                {t("linkLabel")}
                              </a>
                            ) : (
                              <span className="text-muted-foreground">—</span>
                            )}
                          </td>
                          <td className="px-4 py-3">{feedbackDebugBadges(item)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </PageSection>

      <Dialog
        open={selectedItem !== null}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedItem(null);
            setDeleteConfirmOpen(false);
          }
        }}
      >
        <DialogContent className="max-h-[min(90vh,720px)] overflow-y-auto sm:max-w-lg">
          {selectedItem ? (
            <>
              <DialogHeader>
                <DialogTitle>
                  {t("detailTitle", {
                    type: typeLabelFor(selectedItem),
                    date: formatItemDate(selectedItem),
                  })}
                </DialogTitle>
                <DialogDescription className="sr-only">
                  {t("detailDescription")} — {selectedItem.id}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 text-sm">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {t("detailUser")}
                  </p>
                  <p className="mt-1">{selectedItem.username ?? "—"}</p>
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {t("colStatus")}
                  </p>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <FeedbackStatusBadge status={selectedItem.status} labels={statusLabels} />
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selectedItem.status === "new" ? (
                      <>
                        <Button
                          type="button"
                          size="sm"
                          disabled={isUpdatingStatus || isDeletingFeedback}
                          onClick={() => void handleStatusUpdate("read")}
                        >
                          {t("markAsRead")}
                        </Button>
                        <Button
                          type="button"
                          variant="secondary"
                          size="sm"
                          disabled={isUpdatingStatus || isDeletingFeedback}
                          onClick={() => void handleStatusUpdate("resolved")}
                        >
                          {t("markAsResolved")}
                        </Button>
                      </>
                    ) : null}
                    {selectedItem.status === "read" ? (
                      <>
                        <Button
                          type="button"
                          size="sm"
                          disabled={isUpdatingStatus || isDeletingFeedback}
                          onClick={() => void handleStatusUpdate("resolved")}
                        >
                          {t("markAsResolved")}
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={isUpdatingStatus || isDeletingFeedback}
                          onClick={() => void handleStatusUpdate("new")}
                        >
                          {t("reopen")}
                        </Button>
                      </>
                    ) : null}
                    {selectedItem.status === "resolved" ? (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        disabled={isUpdatingStatus || isDeletingFeedback}
                        onClick={() => void handleStatusUpdate("new")}
                      >
                        {t("reopen")}
                      </Button>
                    ) : null}
                  </div>
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {t("detailContext")}
                  </p>
                  {selectedItem.exercise_id ||
                  selectedItem.challenge_id ||
                  selectedItem.page_url ? (
                    <ul className="mt-2 list-inside list-disc space-y-1">
                      {selectedItem.exercise_id ? (
                        <li>
                          <Link
                            href={`/exercises/${selectedItem.exercise_id}`}
                            className="text-primary hover:underline"
                          >
                            {t("linkExercise", { id: selectedItem.exercise_id })}
                          </Link>
                        </li>
                      ) : null}
                      {selectedItem.challenge_id ? (
                        <li>
                          <Link
                            href={`/challenge/${selectedItem.challenge_id}`}
                            className="text-primary hover:underline"
                          >
                            {t("linkChallenge", { id: selectedItem.challenge_id })}
                          </Link>
                        </li>
                      ) : null}
                      {selectedItem.page_url ? (
                        <li>
                          <a
                            href={selectedItem.page_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-primary hover:underline"
                          >
                            <ExternalLink className="h-3 w-3" />
                            {t("detailPage")}
                          </a>
                        </li>
                      ) : null}
                    </ul>
                  ) : (
                    <p className="mt-2 text-muted-foreground">—</p>
                  )}
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {t("detailDebug")}
                  </p>
                  <div className="mt-2">{feedbackDebugBadges(selectedItem)}</div>
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {t("detailDescription")}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {t("detailDescriptionLabel")}
                  </p>
                  <div className="mt-2 whitespace-pre-wrap rounded-md border bg-muted/30 p-3 text-foreground">
                    {selectedItem.description?.trim() ? (
                      selectedItem.description
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="border-t pt-4">
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  disabled={isUpdatingStatus || isDeletingFeedback}
                  onClick={() => setDeleteConfirmOpen(true)}
                >
                  {t("delete")}
                </Button>
              </div>
              <DialogFooter className="gap-2 sm:gap-0">
                <Button type="button" variant="outline" onClick={() => setSelectedItem(null)}>
                  {t("close")}
                </Button>
                <Button type="button" variant="secondary" onClick={handleCopyDetails}>
                  <Copy className="mr-2 h-4 w-4" aria-hidden />
                  {t("copyDetails")}
                </Button>
              </DialogFooter>
            </>
          ) : null}
        </DialogContent>
      </Dialog>

      <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <DialogContent className="sm:max-w-md" showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>{t("deleteConfirmTitle")}</DialogTitle>
            <DialogDescription>{t("deleteConfirmDescription")}</DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2 sm:justify-end">
            <Button
              type="button"
              variant="outline"
              disabled={isDeletingFeedback}
              onClick={() => setDeleteConfirmOpen(false)}
            >
              {t("cancel")}
            </Button>
            <Button
              type="button"
              variant="destructive"
              disabled={isDeletingFeedback}
              onClick={() => void handleConfirmDelete()}
            >
              {t("deleteConfirmAction")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
