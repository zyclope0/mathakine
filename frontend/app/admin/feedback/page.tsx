"use client";

import { useMemo } from "react";
import { useLocale, useTranslations } from "next-intl";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useAdminFeedback } from "@/hooks/useAdminFeedback";
import { MessageCircle, FileQuestion, AlertTriangle, Bug, ExternalLink } from "lucide-react";

const TYPE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  exercise: FileQuestion,
  challenge: AlertTriangle,
  ui: Bug,
  other: MessageCircle,
};

function localeTag(locale: string): string {
  return locale === "en" ? "en-US" : "fr-FR";
}

export default function AdminFeedbackPage() {
  const t = useTranslations("adminPages.feedback");
  const locale = useLocale();
  const dateLocale = localeTag(locale);
  const { feedback, isLoading, error } = useAdminFeedback();

  const typeLabels = useMemo(
    () => ({
      exercise: t("types.exercise"),
      challenge: t("types.challenge"),
      ui: t("types.ui"),
      other: t("types.other"),
    }),
    [t]
  );

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
                      <th className="px-4 py-3 text-left font-medium">{t("colUser")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colContext")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colDescription")}</th>
                      <th className="px-4 py-3 text-left font-medium">{t("colPage")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {feedback.map((item) => {
                      const Icon = TYPE_ICONS[item.feedback_type] ?? MessageCircle;
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
                            <span className="line-clamp-2">
                              {item.description || <span className="text-muted-foreground">—</span>}
                            </span>
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
    </div>
  );
}
