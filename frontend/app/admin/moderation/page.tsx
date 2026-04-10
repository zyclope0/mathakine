"use client";

import { useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ExerciseEditModal } from "@/components/admin/ExerciseEditModal";
import { ChallengeEditModal } from "@/components/admin/ChallengeEditModal";
import { useAdminModeration } from "@/hooks/useAdminModeration";
import { getChallengeTypeDisplay, getAdminAgeDisplay } from "@/lib/constants/challenges";
import { EXERCISE_TYPE_DISPLAY } from "@/lib/constants/exercises";
import { Bot, BookOpen, Puzzle } from "lucide-react";

function localeTag(locale: string): string {
  return locale === "en" ? "en-US" : "fr-FR";
}

export default function AdminModerationPage() {
  const t = useTranslations("adminPages.moderation");
  const locale = useLocale();
  const dateLocale = localeTag(locale);

  const [typeFilter, setTypeFilter] = useState<"all" | "exercises" | "challenges">("all");
  const [editExerciseId, setEditExerciseId] = useState<number | null>(null);
  const [editChallengeId, setEditChallengeId] = useState<number | null>(null);
  const { exercises, challenges, totalExercises, totalChallenges, isLoading, error, refetch } =
    useAdminModeration(typeFilter);

  return (
    <div className="space-y-8">
      <PageHeader title={t("title")} description={t("description")} />

      <PageSection>
        <Card>
          <CardContent className="pt-6">
            <div className="mb-4 flex items-center justify-between gap-4">
              <Select
                value={typeFilter}
                onValueChange={(v) => setTypeFilter(v as typeof typeFilter)}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder={t("filterPlaceholder")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t("filterAll")}</SelectItem>
                  <SelectItem value="exercises">{t("filterExercises")}</SelectItem>
                  <SelectItem value="challenges">{t("filterChallenges")}</SelectItem>
                </SelectContent>
              </Select>
              <div className="flex gap-2 text-sm text-muted-foreground">
                <span>{t("countsExercises", { count: totalExercises })}</span>
                <span>{t("separator")}</span>
                <span>{t("countsChallenges", { count: totalChallenges })}</span>
              </div>
            </div>

            {error ? (
              <p className="py-8 text-center text-destructive">{t("errorLoading")}</p>
            ) : isLoading ? (
              <LoadingState message={t("loading")} />
            ) : (
              <div className="space-y-8">
                {(typeFilter === "all" || typeFilter === "exercises") && (
                  <section>
                    <h3 className="mb-3 flex items-center gap-2 font-medium">
                      <Bot className="h-4 w-4" />
                      {t("sectionExercises", { count: exercises.length })}
                    </h3>
                    {exercises.length === 0 ? (
                      <p className="rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground">
                        {t("emptyExercises")}
                      </p>
                    ) : (
                      <div className="overflow-x-auto rounded-md border">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b bg-muted/50">
                              <th className="px-4 py-3 text-left font-medium">{t("colTitle")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colType")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colAge")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colStatus")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colDate")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colActions")}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {exercises.map((ex, idx) => (
                              <tr
                                key={ex.id}
                                className={`border-b last:border-0 hover:bg-muted/50 ${idx % 2 === 1 ? "bg-muted/30" : ""}`}
                              >
                                <td className="px-4 py-3 font-medium">{ex.title}</td>
                                <td className="px-4 py-3 text-muted-foreground">
                                  {EXERCISE_TYPE_DISPLAY[
                                    ex.exercise_type?.toLowerCase() as keyof typeof EXERCISE_TYPE_DISPLAY
                                  ] ?? ex.exercise_type}
                                </td>
                                <td className="px-4 py-3">{ex.age_group}</td>
                                <td className="px-4 py-3">
                                  <Badge variant={ex.is_archived ? "outline" : "default"}>
                                    {ex.is_archived ? t("archived") : t("active")}
                                  </Badge>
                                </td>
                                <td className="px-4 py-3 text-muted-foreground text-xs">
                                  {ex.created_at
                                    ? new Date(ex.created_at).toLocaleDateString(dateLocale)
                                    : "-"}
                                </td>
                                <td className="px-4 py-3">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setEditExerciseId(ex.id)}
                                  >
                                    <BookOpen className="mr-1 h-4 w-4" />
                                    {t("edit")}
                                  </Button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </section>
                )}

                {(typeFilter === "all" || typeFilter === "challenges") && (
                  <section>
                    <h3 className="mb-3 flex items-center gap-2 font-medium">
                      <Bot className="h-4 w-4" />
                      {t("sectionChallenges", { count: challenges.length })}
                    </h3>
                    {challenges.length === 0 ? (
                      <p className="rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground">
                        {t("emptyChallenges")}
                      </p>
                    ) : (
                      <div className="overflow-x-auto rounded-md border">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b bg-muted/50">
                              <th className="px-4 py-3 text-left font-medium">{t("colTitle")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colType")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colAge")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colStatus")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colDate")}</th>
                              <th className="px-4 py-3 text-left font-medium">{t("colActions")}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {challenges.map((ch, idx) => (
                              <tr
                                key={ch.id}
                                className={`border-b last:border-0 hover:bg-muted/50 ${idx % 2 === 1 ? "bg-muted/30" : ""}`}
                              >
                                <td className="px-4 py-3 font-medium">{ch.title}</td>
                                <td className="px-4 py-3 text-muted-foreground">
                                  {getChallengeTypeDisplay(ch.challenge_type)}
                                </td>
                                <td className="px-4 py-3">{getAdminAgeDisplay(ch.age_group)}</td>
                                <td className="px-4 py-3">
                                  <Badge variant={ch.is_archived ? "outline" : "default"}>
                                    {ch.is_archived ? t("archived") : t("active")}
                                  </Badge>
                                </td>
                                <td className="px-4 py-3 text-muted-foreground text-xs">
                                  {ch.created_at
                                    ? new Date(ch.created_at).toLocaleDateString(dateLocale)
                                    : "-"}
                                </td>
                                <td className="px-4 py-3">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setEditChallengeId(ch.id)}
                                  >
                                    <Puzzle className="mr-1 h-4 w-4" />
                                    {t("edit")}
                                  </Button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </section>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </PageSection>

      <ExerciseEditModal
        exerciseId={editExerciseId}
        open={editExerciseId !== null}
        onOpenChange={(o) => !o && setEditExerciseId(null)}
        onSaved={refetch}
      />
      <ChallengeEditModal
        challengeId={editChallengeId}
        open={editChallengeId !== null}
        onOpenChange={(o) => !o && setEditChallengeId(null)}
        onSaved={refetch}
      />
    </div>
  );
}
