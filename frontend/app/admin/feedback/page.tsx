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

/** Minimum 44px touch height on narrow viewports; compact on sm+ for dense admin table. */
const ROW_CTRL_CLASS = "min-h-11 h-auto px-3 text-xs sm:min-h-9";
const MODAL_BTN_CLASS = "min-h-11 sm:min-h-9";

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

  const listStats = useMemo(() => {
    const total = feedback.length;
    const newCount = feedback.reduce((acc, item) => acc + (item.status === "new" ? 1 : 0), 0);
    return { total, newCount };
  }, [feedback]);

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
      <div className="space-y-3">
        <PageHeader title={t("title")} description={t("description")} />
        {!error && !isLoading && feedback.length > 0 ? (
          <p className="text-sm text-muted-foreground">
            {t("statsSummary", {
              total: listStats.total,
              newCount: listStats.newCount,
            })}
          </p>
        ) : null}
      </div>

      <PageSection>
        <Card className="border-border/80">
          <CardContent className="px-4 pb-6 pt-4 md:px-6">
            {error ? (
              <p className="py-8 text-center text-destructive">{t("errorLoading")}</p>
            ) : isLoading ? (
              <div className="py-4">
                <LoadingState message={t("loading")} />
              </div>
            ) : feedback.length === 0 ? (
              <div className="rounded-md border border-dashed p-10 text-center text-muted-foreground md:p-12">
                <MessageCircle className="mx-auto mb-3 h-12 w-12 opacity-50" />
                <p>{t("emptyTitle")}</p>
                <p className="mt-1 text-sm">{t("emptyHint")}</p>
              </div>
            ) : (
              <div className="-mx-4 overflow-x-auto md:-mx-6">
                <table className="w-full min-w-[52rem] text-sm" aria-label={t("tableAriaLabel")}>
                  <thead className="sticky top-0 z-[1]">
                    <tr className="border-b bg-muted/90 shadow-[inset_0_-1px_0_0_hsl(var(--border))] backdrop-blur-sm dark:bg-muted/85">
                      <th
                        scope="col"
                        className="px-3 py-2.5 text-left text-xs font-semibold sm:px-4 sm:py-3"
                      >
                        {t("colDate")}
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-2.5 text-left text-xs font-semibold sm:px-4 sm:py-3"
                      >
                        {t("colType")}
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-2.5 text-left text-xs font-semibold sm:px-4 sm:py-3"
                      >
                        {t("colStatus")}
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-2.5 text-left text-xs font-semibold sm:px-4 sm:py-3"
                      >
                        {t("colUser")}
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-2.5 text-left text-xs font-semibold sm:px-4 sm:py-3"
                      >
                        {t("colContext")}
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-2.5 text-left text-xs font-semibold sm:px-4 sm:py-3"
                      >
                        {t("colDescription")}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {feedback.map((item) => {
                      const Icon = TYPE_ICONS[item.feedback_type] ?? MessageCircle;
                      const descTrimmed = item.description?.trim();
                      return (
                        <tr key={item.id} className="border-b last:border-0 hover:bg-muted/40">
                          <td className="align-top whitespace-nowrap px-3 py-2.5 text-muted-foreground sm:px-4 sm:py-3">
                            {item.created_at
                              ? new Date(item.created_at).toLocaleString(dateLocale)
                              : "-"}
                          </td>
                          <td className="align-top px-3 py-2.5 sm:px-4 sm:py-3">
                            <Badge variant="outline" className="flex w-fit items-center gap-1">
                              <Icon className="h-3 w-3" />
                              {typeLabels[item.feedback_type as keyof typeof typeLabels] ??
                                item.feedback_type}
                            </Badge>
                          </td>
                          <td className="align-top px-3 py-2.5 sm:px-4 sm:py-3">
                            <FeedbackStatusBadge status={item.status} labels={statusLabels} />
                          </td>
                          <td className="align-top px-3 py-2.5 sm:px-4 sm:py-3">
                            {item.username ?? <span className="text-muted-foreground">—</span>}
                          </td>
                          <td className="align-top px-3 py-2.5 sm:px-4 sm:py-3">
                            <div className="flex flex-wrap gap-1.5">
                              {item.exercise_id ? (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  asChild
                                  className={ROW_CTRL_CLASS}
                                >
                                  <Link href={`/exercises/${item.exercise_id}`}>
                                    {t("linkExercise", { id: item.exercise_id })}
                                  </Link>
                                </Button>
                              ) : null}
                              {item.challenge_id ? (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  asChild
                                  className={ROW_CTRL_CLASS}
                                >
                                  <Link href={`/challenge/${item.challenge_id}`}>
                                    {t("linkChallenge", { id: item.challenge_id })}
                                  </Link>
                                </Button>
                              ) : null}
                              {!item.exercise_id && !item.challenge_id ? (
                                <span className="inline-flex min-h-11 items-center text-muted-foreground sm:min-h-9">
                                  —
                                </span>
                              ) : null}
                            </div>
                          </td>
                          <td className="max-w-[min(100%,20rem)] align-top px-3 py-2.5 sm:max-w-[24rem] sm:px-4 sm:py-3">
                            <div className="flex flex-col gap-2">
                              <span className="line-clamp-2 text-foreground/90">
                                {descTrimmed ? (
                                  item.description
                                ) : (
                                  <span className="text-muted-foreground">
                                    {t("tableDescriptionPlaceholder")}
                                  </span>
                                )}
                              </span>
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                className={`${ROW_CTRL_CLASS} w-fit shrink-0`}
                                onClick={() => setSelectedItem(item)}
                              >
                                {t("viewDetails")}
                              </Button>
                            </div>
                          </td>
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
              <div className="space-y-6 text-sm">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {t("detailUser")}
                  </p>
                  <p className="mt-1">{selectedItem.username ?? "—"}</p>
                </div>
                <div className="space-y-2">
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {t("sectionTreatment")}
                  </p>
                  <div className="space-y-3 rounded-lg border border-border/70 bg-muted/25 p-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <FeedbackStatusBadge status={selectedItem.status} labels={statusLabels} />
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {selectedItem.status === "new" ? (
                        <>
                          <Button
                            type="button"
                            size="sm"
                            className={MODAL_BTN_CLASS}
                            disabled={isUpdatingStatus || isDeletingFeedback}
                            onClick={() => void handleStatusUpdate("read")}
                          >
                            {t("markAsRead")}
                          </Button>
                          <Button
                            type="button"
                            variant="secondary"
                            size="sm"
                            className={MODAL_BTN_CLASS}
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
                            className={MODAL_BTN_CLASS}
                            disabled={isUpdatingStatus || isDeletingFeedback}
                            onClick={() => void handleStatusUpdate("resolved")}
                          >
                            {t("markAsResolved")}
                          </Button>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            className={MODAL_BTN_CLASS}
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
                          className={MODAL_BTN_CLASS}
                          disabled={isUpdatingStatus || isDeletingFeedback}
                          onClick={() => void handleStatusUpdate("new")}
                        >
                          {t("reopen")}
                        </Button>
                      ) : null}
                    </div>
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
              <div className="border-t border-border/60 pt-5">
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  className={MODAL_BTN_CLASS}
                  disabled={isUpdatingStatus || isDeletingFeedback}
                  onClick={() => setDeleteConfirmOpen(true)}
                >
                  {t("delete")}
                </Button>
              </div>
              <DialogFooter className="mt-2 sm:gap-0">
                <Button
                  type="button"
                  variant="outline"
                  className={MODAL_BTN_CLASS}
                  onClick={() => setSelectedItem(null)}
                >
                  {t("close")}
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  className={MODAL_BTN_CLASS}
                  onClick={handleCopyDetails}
                >
                  <Copy className="mr-2 h-4 w-4 shrink-0" aria-hidden />
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
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              className={MODAL_BTN_CLASS}
              disabled={isDeletingFeedback}
              onClick={() => setDeleteConfirmOpen(false)}
            >
              {t("cancel")}
            </Button>
            <Button
              type="button"
              variant="destructive"
              className={MODAL_BTN_CLASS}
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
