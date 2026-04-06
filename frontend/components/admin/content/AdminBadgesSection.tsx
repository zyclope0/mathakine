"use client";

import { useState } from "react";
import { LoadingState } from "@/components/layout";
import { BadgeEditModal } from "@/components/admin/BadgeEditModal";
import { BadgeCreateModal } from "@/components/admin/BadgeCreateModal";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAdminBadges } from "@/hooks/useAdminBadges";
import { buildBadgeCategoryFilterOptions } from "@/lib/admin/content/adminContentPage";
import { Plus } from "lucide-react";

const BADGE_CATEGORY_FILTER_OPTIONS = buildBadgeCategoryFilterOptions();

export interface AdminBadgesSectionProps {
  initialEditId?: number | null;
}

export function AdminBadgesSection({ initialEditId }: AdminBadgesSectionProps) {
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [editBadgeId, setEditBadgeId] = useState<number | null>(initialEditId ?? null);
  const [createBadgeOpen, setCreateBadgeOpen] = useState(false);

  const { badges, isLoading, error, refetch } = useAdminBadges();

  const filtered = badges.filter((b) => {
    if (activeFilter === "true" && !b.is_active) return false;
    if (activeFilter === "false" && b.is_active) return false;
    if (categoryFilter !== "all" && (b.category || "") !== categoryFilter) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:flex-wrap">
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Catégorie" />
          </SelectTrigger>
          <SelectContent>
            {BADGE_CATEGORY_FILTER_OPTIONS.map((c) => (
              <SelectItem key={c.value} value={c.value}>
                {c.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={activeFilter} onValueChange={setActiveFilter}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Statut" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous</SelectItem>
            <SelectItem value="true">Actifs</SelectItem>
            <SelectItem value="false">Inactifs</SelectItem>
          </SelectContent>
        </Select>
        <Button onClick={() => setCreateBadgeOpen(true)}>
          <Plus className="h-4 w-4 mr-1" />
          Créer un badge
        </Button>
      </div>

      {error ? (
        <p className="py-8 text-center text-destructive">
          Erreur de chargement. Vérifiez vos droits.
        </p>
      ) : isLoading ? (
        <LoadingState message="Chargement des badges..." />
      ) : (
        <div className="overflow-x-auto rounded-md border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left font-medium">Code</th>
                <th className="px-4 py-3 text-left font-medium">Nom</th>
                <th className="px-4 py-3 text-left font-medium">Catégorie</th>
                <th className="px-4 py-3 text-left font-medium">Difficulté</th>
                <th className="px-4 py-3 text-left font-medium">Points</th>
                <th className="px-4 py-3 text-left font-medium">Utilisateurs</th>
                <th className="px-4 py-3 text-left font-medium">Statut</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-muted-foreground">
                    Aucun badge trouvé
                  </td>
                </tr>
              ) : (
                filtered.map((b, idx) => (
                  <tr
                    key={b.id}
                    className={`border-b last:border-0 cursor-pointer hover:bg-muted/50 transition-colors ${idx % 2 === 1 ? "bg-muted/30" : ""}`}
                    onClick={() => setEditBadgeId(b.id)}
                  >
                    <td className="px-4 py-3 font-mono text-xs">{b.code}</td>
                    <td className="px-4 py-3 font-medium">{b.name}</td>
                    <td className="px-4 py-3 text-muted-foreground">{b.category || "-"}</td>
                    <td className="px-4 py-3">{b.difficulty || "bronze"}</td>
                    <td className="px-4 py-3">{b.points_reward ?? 0}</td>
                    <td className="px-4 py-3">{b._user_count ?? 0}</td>
                    <td className="px-4 py-3">
                      <Badge variant={b.is_active ? "default" : "outline"}>
                        {b.is_active ? "Actif" : "Inactif"}
                      </Badge>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <BadgeCreateModal
        open={createBadgeOpen}
        onOpenChange={setCreateBadgeOpen}
        onCreated={refetch}
      />
      <BadgeEditModal
        badgeId={editBadgeId}
        open={editBadgeId !== null}
        onOpenChange={(o) => !o && setEditBadgeId(null)}
        onSaved={refetch}
      />
    </div>
  );
}
