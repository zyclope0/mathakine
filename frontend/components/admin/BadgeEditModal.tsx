"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronDown, ChevronUp, Info, RotateCcw, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api/client";
import type { AdminBadge } from "@/hooks/useAdminBadges";

const CATEGORIES = ["progression", "mastery", "special", "performance", "regularity", "discovery"];
const DIFFICULTIES = ["bronze", "silver", "gold", "legendary"];

const REQUIREMENT_EXAMPLES = [
  { label: "Tentatives", value: '{"attempts_count": 10}' },
  { label: "Taux réussite", value: '{"min_attempts": 50, "success_rate": 80}' },
  { label: "Jours consécutifs", value: '{"consecutive_days": 7}' },
  { label: "Temps max", value: '{"max_time": 5}' },
  { label: "Défis logiques (B5)", value: '{"logic_attempts_count": 10}' },
  {
    label: "Mixte exercices+défis (B5)",
    value: '{"attempts_count": 20, "logic_attempts_count": 5}',
  },
  { label: "Comeback (7j)", value: '{"comeback_days": 7}' },
];

interface BadgeEditModalProps {
  badgeId: number | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
  onDeleted?: () => void;
}

export function BadgeEditModal({
  badgeId,
  open,
  onOpenChange,
  onSaved,
  onDeleted,
}: BadgeEditModalProps) {
  const [data, setData] = useState<AdminBadge | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [principlesOpen, setPrinciplesOpen] = useState(false);

  useEffect(() => {
    if (!open || !badgeId) return;
    setErrors({});
    setLoading(true);
    api
      .get<AdminBadge>(`/api/admin/badges/${badgeId}`)
      .then((res) => setData(res))
      .catch(() => toast.error("Erreur de chargement"))
      .finally(() => setLoading(false));
  }, [open, badgeId]);

  const requirementsStr =
    data?.requirements != null
      ? typeof data.requirements === "string"
        ? data.requirements
        : JSON.stringify(data.requirements as Record<string, unknown>, null, 2)
      : "{}";

  const validate = (): boolean => {
    if (!data) return false;
    const e: Record<string, string> = {};
    if (!data.name?.trim()) e.name = "Le nom est obligatoire";
    try {
      const req =
        typeof data.requirements === "string"
          ? JSON.parse(data.requirements || "{}")
          : data.requirements;
      if (!req || typeof req !== "object" || Object.keys(req).length === 0)
        e.requirements = "requirements doit contenir un schéma valide";
    } catch {
      e.requirements = "JSON invalide";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSave = async () => {
    if (!data) return;
    if (!validate()) {
      toast.error("Champs incomplets", { description: "Vérifiez les champs obligatoires." });
      return;
    }
    setSaving(true);
    try {
      let requirements: Record<string, unknown>;
      try {
        requirements =
          typeof data.requirements === "string"
            ? (JSON.parse(data.requirements) as Record<string, unknown>)
            : ((data.requirements as Record<string, unknown>) ?? {});
      } catch {
        toast.error("Requirements JSON invalide");
        setSaving(false);
        return;
      }
      await api.put(`/api/admin/badges/${data.id}`, {
        name: data.name.trim(),
        description: data.description || "",
        icon_url: data.icon_url || "",
        category: data.category || "",
        difficulty: data.difficulty || "bronze",
        points_reward: data.points_reward ?? 0,
        is_secret: data.is_secret,
        requirements,
        star_wars_title: data.star_wars_title || "",
        is_active: data.is_active,
      });
      toast.success("Badge mis à jour");
      onOpenChange(false);
      onSaved();
    } catch (err) {
      toast.error("Erreur", {
        description: err instanceof Error ? err.message : "Échec de la sauvegarde",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!data || !confirm(`Désactiver le badge « ${data.name} » ? (soft delete)`)) return;
    setDeleting(true);
    try {
      await api.delete(`/api/admin/badges/${data.id}`);
      toast.success("Badge désactivé");
      onOpenChange(false);
      onSaved();
      onDeleted?.();
    } catch (err) {
      toast.error("Erreur", {
        description: err instanceof Error ? err.message : "Échec de la suppression",
      });
    } finally {
      setDeleting(false);
    }
  };

  const handleReactivate = async () => {
    if (!data) return;
    setSaving(true);
    try {
      await api.put(`/api/admin/badges/${data.id}`, { is_active: true });
      toast.success("Badge réactivé");
      setData((d) => (d ? { ...d, is_active: true } : d));
      onSaved();
    } catch (err) {
      toast.error("Erreur", {
        description: err instanceof Error ? err.message : "Échec de la réactivation",
      });
    } finally {
      setSaving(false);
    }
  };

  const update = (k: keyof AdminBadge, v: unknown) => {
    if (!data) return;
    setData({ ...data, [k]: v });
    if (errors[k as string]) setErrors((prev) => ({ ...prev, [k]: "" }));
  };

  if (loading || !data) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Chargement du badge</DialogTitle>
          </DialogHeader>
          <div className="py-12 text-center text-muted-foreground">Chargement...</div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Modifier le badge — {data.code}</DialogTitle>
        </DialogHeader>

        <div className="mb-4">
          <Button
            variant="outline"
            size="sm"
            className="w-full justify-between"
            onClick={() => setPrinciplesOpen(!principlesOpen)}
          >
            <span className="flex items-center gap-2">
              <Info className="h-4 w-4" />
              Principes psychologiques — design des badges
            </span>
            {principlesOpen ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
          {principlesOpen && (
            <div className="rounded-md border bg-muted/50 p-3 text-sm space-y-1.5 mt-2">
              <p>
                <strong>Goal-gradient :</strong> Objectif progressif (X/Y), barre visible, « Plus
                que X » — incite à l&apos;effort
              </p>
              <p>
                <strong>Endowment :</strong> Visuel valorisant pour les badges obtenus, option
                épingler — renforce la propriété perçue
              </p>
              <p>
                <strong>Scarcity :</strong> Badges or/légendaire = visuels distincts ; « Rare »
                (&lt;5%) — rareté motive
              </p>
              <p>
                <strong>Social proof :</strong> « X% ont débloqué » — comparaison avec les pairs
                renforce le désir
              </p>
              <p>
                <strong>Loss aversion :</strong> Streaks, « Tu approches, ne lâche pas ! » — peur de
                perdre motive 2× plus
              </p>
              <p className="pt-2 mt-2 border-t border-border/50">
                <strong>Visuel (sans SW) :</strong> Emoji ou URL, nom évocateur — esprit
                progression/maîtrise
              </p>
            </div>
          )}
        </div>

        <div className="grid gap-4 py-2">
          <div className="grid gap-2">
            <Label>Code (non modifiable)</Label>
            <Input value={data.code} disabled className="bg-muted" />
          </div>

          <div className="grid gap-2">
            <Label>
              Nom <span className="text-destructive">*</span>
            </Label>
            <Input
              value={data.name}
              onChange={(e) => update("name", e.target.value)}
              className={errors.name ? "border-destructive" : ""}
            />
            {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
          </div>

          <div className="grid gap-2">
            <Label>Description</Label>
            <Textarea
              value={data.description || ""}
              onChange={(e) => update("description", e.target.value)}
              rows={2}
            />
          </div>

          <div className="grid gap-2">
            <Label>Icône (emoji ou URL)</Label>
            <Input
              value={data.icon_url || ""}
              onChange={(e) => update("icon_url", e.target.value)}
              placeholder="✨ ou https://..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label>Catégorie</Label>
              <Select
                value={data.category || "progression"}
                onValueChange={(v) => update("category", v)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map((c) => (
                    <SelectItem key={c} value={c}>
                      {c}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>Difficulté</Label>
              <Select
                value={data.difficulty || "bronze"}
                onValueChange={(v) => update("difficulty", v)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DIFFICULTIES.map((d) => (
                    <SelectItem key={d} value={d}>
                      {d}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label>Points</Label>
              <Input
                type="number"
                min={0}
                value={data.points_reward ?? 0}
                onChange={(e) => update("points_reward", parseInt(e.target.value, 10) || 0)}
              />
            </div>
            <div className="grid gap-2">
              <Label>Titre Star Wars</Label>
              <Input
                value={data.star_wars_title || ""}
                onChange={(e) => update("star_wars_title", e.target.value)}
              />
            </div>
          </div>

          <div className="grid gap-2">
            <div className="flex items-center justify-between">
              <Label>
                Requirements (JSON) <span className="text-destructive">*</span>
              </Label>
              <div className="flex gap-1 flex-wrap">
                {REQUIREMENT_EXAMPLES.map((ex) => (
                  <Button
                    key={ex.value}
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-7 text-xs"
                    onClick={() => update("requirements", ex.value)}
                  >
                    {ex.label}
                  </Button>
                ))}
              </div>
            </div>
            <Textarea
              value={requirementsStr}
              onChange={(e) => update("requirements", e.target.value)}
              rows={3}
              className={`font-mono text-sm ${errors.requirements ? "border-destructive" : ""}`}
            />
            {errors.requirements && (
              <p className="text-sm text-destructive">{errors.requirements}</p>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="edit_is_secret"
                checked={data.is_secret}
                onChange={(e) => update("is_secret", e.target.checked)}
                className="rounded"
                aria-label="Badge secret"
              />
              <Label htmlFor="edit_is_secret">Badge secret</Label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="edit_is_active"
                checked={data.is_active}
                onChange={(e) => update("is_active", e.target.checked)}
                className="rounded"
                aria-label="Actif"
              />
              <Label htmlFor="edit_is_active">Actif</Label>
            </div>
          </div>

          {data._user_count != null && data._user_count > 0 && (
            <p className="text-sm text-muted-foreground">
              {data._user_count} utilisateur{(data._user_count ?? 0) > 1 ? "s" : ""} ont ce badge
            </p>
          )}
        </div>

        <DialogFooter>
          {data.is_active ? (
            <Button variant="destructive" onClick={handleDelete} disabled={saving || deleting}>
              <Trash2 className="h-4 w-4 mr-1" />
              {deleting ? "Désactivation..." : "Désactiver"}
            </Button>
          ) : (
            <Button variant="outline" onClick={handleReactivate} disabled={saving || deleting}>
              <RotateCcw className="h-4 w-4 mr-1" />
              {saving ? "Réactivation..." : "Réactiver"}
            </Button>
          )}
          <div className="flex-1" />
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Annuler
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Enregistrement..." : "Enregistrer"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
