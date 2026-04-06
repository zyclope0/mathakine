"use client";

import { useState } from "react";
import { LoadingState } from "@/components/layout";
import { ExerciseEditModal } from "@/components/admin/ExerciseEditModal";
import { ExerciseCreateModal } from "@/components/admin/ExerciseCreateModal";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAdminExercises } from "@/hooks/useAdminExercises";
import {
  buildExerciseTypeFilterOptions,
  ADMIN_CONTENT_PAGE_SIZE,
} from "@/lib/admin/content/adminContentPage";
import {
  getAdminExerciseAgeGroupListDisplay,
  getAdminExerciseDifficultyDisplay,
  getAdminExerciseTypeDisplay,
} from "@/lib/admin/exercises/adminExerciseCoherence";
import { Archive, ChevronLeft, ChevronRight, Plus, RotateCcw, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { AdminContentSortIcon } from "@/components/admin/content/AdminContentSortIcon";

const EXERCISE_TYPE_FILTER_OPTIONS = buildExerciseTypeFilterOptions();

export interface AdminExercisesSectionProps {
  initialEditId?: number | null;
}

export function AdminExercisesSection({ initialEditId }: AdminExercisesSectionProps) {
  const [archivedFilter, setArchivedFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("created_at");
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(0);
  const [editExerciseId, setEditExerciseId] = useState<number | null>(initialEditId ?? null);
  const [createExerciseOpen, setCreateExerciseOpen] = useState(false);

  const archived = archivedFilter === "all" ? undefined : archivedFilter === "true";
  const { exercises, total, isLoading, error, refetch, updateArchived, isUpdating } =
    useAdminExercises({
      ...(archived !== undefined && { archived }),
      ...(typeFilter !== "all" && { type: typeFilter }),
      ...(search.trim() && { search: search.trim() }),
      sort,
      order,
      skip: page * ADMIN_CONTENT_PAGE_SIZE,
      limit: ADMIN_CONTENT_PAGE_SIZE,
    });

  const toggleSort = (col: string) => {
    if (sort === col) setOrder((o) => (o === "asc" ? "desc" : "asc"));
    else {
      setSort(col);
      setOrder("asc");
    }
    setPage(0);
  };

  const handleToggleArchived = async (ex: { id: number; title: string; is_archived: boolean }) => {
    try {
      await updateArchived({
        exerciseId: ex.id,
        isArchived: !ex.is_archived,
      });
      toast.success(ex.is_archived ? "Exercice réactivé" : "Exercice archivé", {
        description: `${ex.title} a été ${ex.is_archived ? "réactivé" : "archivé"}.`,
      });
    } catch (err) {
      toast.error("Erreur", {
        description: err instanceof Error ? err.message : "Erreur lors de la mise à jour",
      });
    }
  };

  const totalPages = Math.ceil(total / ADMIN_CONTENT_PAGE_SIZE) || 1;

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:flex-wrap">
        <div className="flex-1 min-w-[200px]">
          <Label htmlFor="ex-search" className="sr-only">
            Rechercher
          </Label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="ex-search"
              placeholder="Rechercher par titre..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(0);
              }}
              className="pl-9"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <Select
            value={typeFilter}
            onValueChange={(v) => {
              setTypeFilter(v);
              setPage(0);
            }}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              {EXERCISE_TYPE_FILTER_OPTIONS.map((t) => (
                <SelectItem key={t.value} value={t.value}>
                  {t.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={archivedFilter}
            onValueChange={(v) => {
              setArchivedFilter(v);
              setPage(0);
            }}
          >
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Statut" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous</SelectItem>
              <SelectItem value="false">Actifs</SelectItem>
              <SelectItem value="true">Archivés</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={() => setCreateExerciseOpen(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Créer un exercice
          </Button>
        </div>
      </div>

      {error ? (
        <p className="py-8 text-center text-destructive">
          Erreur de chargement. Vérifiez vos droits.
        </p>
      ) : isLoading ? (
        <LoadingState message="Chargement des exercices..." />
      ) : (
        <>
          <div className="overflow-x-auto rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left font-medium">
                    <button
                      type="button"
                      onClick={() => toggleSort("title")}
                      className="flex items-center hover:underline"
                    >
                      Titre <AdminContentSortIcon col="title" sort={sort} order={order} />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left font-medium">
                    <button
                      type="button"
                      onClick={() => toggleSort("exercise_type")}
                      className="flex items-center hover:underline"
                    >
                      Type <AdminContentSortIcon col="exercise_type" sort={sort} order={order} />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left font-medium">
                    <button
                      type="button"
                      onClick={() => toggleSort("difficulty")}
                      className="flex items-center hover:underline"
                    >
                      Difficulté <AdminContentSortIcon col="difficulty" sort={sort} order={order} />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left font-medium">
                    <button
                      type="button"
                      onClick={() => toggleSort("age_group")}
                      className="flex items-center hover:underline"
                    >
                      Âge <AdminContentSortIcon col="age_group" sort={sort} order={order} />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left font-medium">Tentatives</th>
                  <th className="px-4 py-3 text-left font-medium">Succès</th>
                  <th className="px-4 py-3 text-left font-medium">Statut</th>
                  <th className="px-4 py-3 text-left font-medium">
                    <button
                      type="button"
                      onClick={() => toggleSort("created_at")}
                      className="flex items-center hover:underline"
                    >
                      Date <AdminContentSortIcon col="created_at" sort={sort} order={order} />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {exercises.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-12 text-center text-muted-foreground">
                      Aucun exercice trouvé
                    </td>
                  </tr>
                ) : (
                  exercises.map((ex, idx) => (
                    <tr
                      key={ex.id}
                      className={`border-b last:border-0 cursor-pointer hover:bg-muted/50 transition-colors ${idx % 2 === 1 ? "bg-muted/30" : ""}`}
                      onClick={() => setEditExerciseId(ex.id)}
                    >
                      <td className="px-4 py-3 font-medium">{ex.title}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {getAdminExerciseTypeDisplay(ex.exercise_type)}
                      </td>
                      <td className="px-4 py-3">
                        {getAdminExerciseDifficultyDisplay(
                          ex.difficulty,
                          ex.difficulty_tier != null
                            ? { difficultyTier: ex.difficulty_tier }
                            : undefined
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {getAdminExerciseAgeGroupListDisplay(ex.age_group)}
                      </td>
                      <td className="px-4 py-3">{ex.attempt_count}</td>
                      <td className="px-4 py-3">{ex.success_rate}%</td>
                      <td className="px-4 py-3">
                        <Badge variant={ex.is_archived ? "outline" : "default"}>
                          {ex.is_archived ? "Archivé" : "Actif"}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">
                        {ex.created_at ? new Date(ex.created_at).toLocaleDateString("fr-FR") : "-"}
                      </td>
                      <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleToggleArchived(ex)}
                          disabled={isUpdating}
                          title={ex.is_archived ? "Réactiver l'exercice" : "Archiver l'exercice"}
                        >
                          {ex.is_archived ? (
                            <>
                              <RotateCcw className="mr-1 h-4 w-4" />
                              Réactiver
                            </>
                          ) : (
                            <>
                              <Archive className="mr-1 h-4 w-4" />
                              Archiver
                            </>
                          )}
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                {total} exercice{total > 1 ? "s" : ""} — Page {page + 1} / {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  disabled={page === 0}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Précédent
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                  disabled={page >= totalPages - 1}
                >
                  Suivant
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}
      <ExerciseCreateModal
        open={createExerciseOpen}
        onOpenChange={setCreateExerciseOpen}
        onCreated={refetch}
      />
      <ExerciseEditModal
        exerciseId={editExerciseId}
        open={editExerciseId !== null}
        onOpenChange={(o) => !o && setEditExerciseId(null)}
        onSaved={refetch}
      />
    </div>
  );
}
