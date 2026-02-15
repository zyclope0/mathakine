"use client";

import { useState } from "react";
import Link from "next/link";
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
import { useAdminModeration } from "@/hooks/useAdminModeration";
import { getChallengeTypeDisplay, getAdminAgeDisplay } from "@/lib/constants/challenges";
import { EXERCISE_TYPE_DISPLAY } from "@/lib/constants/exercises";
import { Bot, BookOpen, Puzzle } from "lucide-react";

export default function AdminModerationPage() {
  const [typeFilter, setTypeFilter] = useState<"all" | "exercises" | "challenges">("all");
  const {
    exercises,
    challenges,
    totalExercises,
    totalChallenges,
    isLoading,
    error,
  } = useAdminModeration(typeFilter);

  return (
    <>
      <PageHeader
        title="Modération IA"
        description="Contenu généré par intelligence artificielle — validation et suivi"
      />

      <PageSection>
        <Card>
          <CardContent className="pt-6">
            <div className="mb-4 flex items-center justify-between gap-4">
              <Select value={typeFilter} onValueChange={(v) => setTypeFilter(v as typeof typeFilter)}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Type de contenu" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Exercices et défis</SelectItem>
                  <SelectItem value="exercises">Exercices seulement</SelectItem>
                  <SelectItem value="challenges">Défis seulement</SelectItem>
                </SelectContent>
              </Select>
              <div className="flex gap-2 text-sm text-muted-foreground">
                <span>{totalExercises} exercice(s) IA</span>
                <span>•</span>
                <span>{totalChallenges} défi(s) IA</span>
              </div>
            </div>

            {error ? (
              <p className="py-8 text-center text-destructive">
                Erreur de chargement. Vérifiez vos droits.
              </p>
            ) : isLoading ? (
              <LoadingState message="Chargement du contenu IA..." />
            ) : (
              <div className="space-y-8">
                {(typeFilter === "all" || typeFilter === "exercises") && (
                  <section>
                    <h3 className="mb-3 flex items-center gap-2 font-medium">
                      <Bot className="h-4 w-4" />
                      Exercices générés par IA ({exercises.length})
                    </h3>
                    {exercises.length === 0 ? (
                      <p className="rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground">
                        Aucun exercice généré par IA.
                      </p>
                    ) : (
                      <div className="overflow-x-auto rounded-md border">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b bg-muted/50">
                              <th className="px-4 py-3 text-left font-medium">Titre</th>
                              <th className="px-4 py-3 text-left font-medium">Type</th>
                              <th className="px-4 py-3 text-left font-medium">Âge</th>
                              <th className="px-4 py-3 text-left font-medium">Statut</th>
                              <th className="px-4 py-3 text-left font-medium">Date</th>
                              <th className="px-4 py-3 text-left font-medium">Actions</th>
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
                                  {EXERCISE_TYPE_DISPLAY[ex.exercise_type?.toLowerCase() as keyof typeof EXERCISE_TYPE_DISPLAY] ?? ex.exercise_type}
                                </td>
                                <td className="px-4 py-3">{ex.age_group}</td>
                                <td className="px-4 py-3">
                                  <Badge variant={ex.is_archived ? "outline" : "default"}>
                                    {ex.is_archived ? "Archivé" : "Actif"}
                                  </Badge>
                                </td>
                                <td className="px-4 py-3 text-muted-foreground text-xs">
                                  {ex.created_at ? new Date(ex.created_at).toLocaleDateString("fr-FR") : "-"}
                                </td>
                                <td className="px-4 py-3">
                                  <Button variant="outline" size="sm" asChild>
                                    <Link href={`/admin/content?tab=exercises&edit=${ex.id}`}>
                                      <BookOpen className="mr-1 h-4 w-4" />
                                      Éditer
                                    </Link>
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
                      Défis générés par IA ({challenges.length})
                    </h3>
                    {challenges.length === 0 ? (
                      <p className="rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground">
                        Aucun défi généré par IA.
                      </p>
                    ) : (
                      <div className="overflow-x-auto rounded-md border">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b bg-muted/50">
                              <th className="px-4 py-3 text-left font-medium">Titre</th>
                              <th className="px-4 py-3 text-left font-medium">Type</th>
                              <th className="px-4 py-3 text-left font-medium">Âge</th>
                              <th className="px-4 py-3 text-left font-medium">Statut</th>
                              <th className="px-4 py-3 text-left font-medium">Date</th>
                              <th className="px-4 py-3 text-left font-medium">Actions</th>
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
                                    {ch.is_archived ? "Archivé" : "Actif"}
                                  </Badge>
                                </td>
                                <td className="px-4 py-3 text-muted-foreground text-xs">
                                  {ch.created_at ? new Date(ch.created_at).toLocaleDateString("fr-FR") : "-"}
                                </td>
                                <td className="px-4 py-3">
                                  <Button variant="outline" size="sm" asChild>
<Link href={`/admin/content?tab=challenges&edit=${ch.id}`}>
                                    <Puzzle className="mr-1 h-4 w-4" />
                                      Éditer
                                    </Link>
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
    </>
  );
}
