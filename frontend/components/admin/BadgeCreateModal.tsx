"use client";

import { useState } from "react";
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
import { ChevronDown, ChevronUp, Info } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api/client";

const CATEGORIES = ["progression", "mastery", "special", "performance", "regularity", "discovery"];
const DIFFICULTIES = ["bronze", "silver", "gold", "legendary"];

const REQUIREMENT_EXAMPLES = [
  { label: "Tentatives (ex: 10)", value: '{"attempts_count": 10}' },
  { label: "Taux réussite (ex: 50 tentatives, 80%)", value: '{"min_attempts": 50, "success_rate": 80}' },
  { label: "Jours consécutifs (ex: 7)", value: '{"consecutive_days": 7}' },
  { label: "Temps max (ex: 5s)", value: '{"max_time": 5}' },
  { label: "Défis logiques (ex: 10) — B5", value: '{"logic_attempts_count": 10}' },
  { label: "Mixte (ex: 20 exercices + 5 défis) — B5", value: '{"attempts_count": 20, "logic_attempts_count": 5}' },
  { label: "Comeback (7j sans activité)", value: '{"comeback_days": 7}' },
];

interface BadgeCreateModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}

const initialState = {
  code: "",
  name: "",
  description: "",
  icon_url: "",
  category: "progression",
  difficulty: "bronze",
  points_reward: 10,
  is_secret: false,
  requirements: '{"attempts_count": 10}' as string,
  star_wars_title: "",
};

export function BadgeCreateModal({
  open,
  onOpenChange,
  onCreated,
}: BadgeCreateModalProps) {
  const [data, setData] = useState(initialState);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [principlesOpen, setPrinciplesOpen] = useState(false);

  const update = (k: keyof typeof initialState, v: unknown) => {
    setData((prev) => ({ ...prev, [k]: v }));
    if (errors[k as string]) setErrors((prev) => ({ ...prev, [k]: "" }));
  };

  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!data.code.trim()) e.code = "Le code est obligatoire";
    else if (!/^[a-z0-9_]+$/.test(data.code.replace(/\s/g, "_")))
      e.code = "Code : lettres minuscules, chiffres et underscores uniquement";
    if (!data.name.trim()) e.name = "Le nom est obligatoire";
    try {
      const req = JSON.parse(data.requirements || "{}");
      if (!req || typeof req !== "object" || Object.keys(req).length === 0)
        e.requirements = "requirements doit contenir un schéma valide (ex: attempts_count)";
    } catch {
      e.requirements = "JSON invalide";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleCreate = async () => {
    if (!validate()) {
      toast.error("Champs incomplets", { description: "Vérifiez les champs obligatoires." });
      return;
    }
    setSaving(true);
    try {
      let requirements: Record<string, unknown>;
      try {
        requirements = JSON.parse(data.requirements) as Record<string, unknown>;
      } catch {
        toast.error("Requirements JSON invalide");
        setSaving(false);
        return;
      }
      await api.post("/api/admin/badges", {
        code: data.code.trim().toLowerCase().replace(/\s/g, "_"),
        name: data.name.trim(),
        description: data.description.trim() || undefined,
        icon_url: data.icon_url.trim() || undefined,
        category: data.category || undefined,
        difficulty: data.difficulty || "bronze",
        points_reward: Number(data.points_reward) || 0,
        is_secret: data.is_secret,
        requirements,
        star_wars_title: data.star_wars_title.trim() || undefined,
      });
      toast.success("Badge créé");
      setData(initialState);
      onOpenChange(false);
      onCreated();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Échec de la création";
      toast.error("Erreur", { description: msg });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Créer un badge</DialogTitle>
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
            {principlesOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
          {principlesOpen && (
            <div className="rounded-md border bg-muted/50 p-3 text-sm space-y-1.5 mt-2">
              <p><strong>Goal-gradient :</strong> Objectif progressif (X/Y), barre visible, « Plus que X » — incite à l&apos;effort</p>
              <p><strong>Endowment :</strong> Visuel valorisant pour les badges obtenus, option épingler — renforce la propriété perçue</p>
              <p><strong>Scarcity :</strong> Badges or/légendaire = visuels distincts ; « Rare » (&lt;5%) — rareté motive</p>
              <p><strong>Social proof :</strong> « X% ont débloqué » — comparaison avec les pairs renforce le désir</p>
              <p><strong>Loss aversion :</strong> Streaks, « Tu approches, ne lâche pas ! » — peur de perdre motive 2× plus</p>
              <p className="pt-2 mt-2 border-t border-border/50"><strong>Visuel (sans SW) :</strong> Emoji ou URL (✨ ⚡ 🎯 🌟), nom évocateur (Apprenti des Nombres, Maître des Sommes) — esprit progression/maîtrise</p>
            </div>
          )}
        </div>

        <div className="grid gap-4 py-2">
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label>Code <span className="text-destructive">*</span></Label>
              <Input
                value={data.code}
                onChange={(e) => update("code", e.target.value)}
                placeholder="ex: premiers_pas"
                className={errors.code ? "border-destructive" : ""}
              />
              {errors.code && <p className="text-sm text-destructive">{errors.code}</p>}
            </div>
            <div className="grid gap-2">
              <Label>Nom <span className="text-destructive">*</span></Label>
              <Input
                value={data.name}
                onChange={(e) => update("name", e.target.value)}
                placeholder="Premiers Pas"
                className={errors.name ? "border-destructive" : ""}
              />
              {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
            </div>
          </div>

          <div className="grid gap-2">
            <Label>Description</Label>
            <Textarea
              value={data.description}
              onChange={(e) => update("description", e.target.value)}
              rows={2}
              placeholder="Résous ton premier exercice"
            />
          </div>

          <div className="grid gap-2">
            <Label>Icône (emoji ou URL)</Label>
            <Input
              value={data.icon_url}
              onChange={(e) => update("icon_url", e.target.value)}
              placeholder="✨ ou https://..."
            />
            <p className="text-xs text-muted-foreground">Emoji (ex: ✨ ⚡ 🎯 🌟) ou URL d&apos;image — esprit progression sans droits d&apos;auteur</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label>Catégorie</Label>
              <Select value={data.category} onValueChange={(v) => update("category", v)}>
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
              <Select value={data.difficulty} onValueChange={(v) => update("difficulty", v)}>
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
                value={data.points_reward}
                onChange={(e) => update("points_reward", e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label>Titre Star Wars</Label>
              <Input
                value={data.star_wars_title}
                onChange={(e) => update("star_wars_title", e.target.value)}
                placeholder="Éveil de la Force"
              />
            </div>
          </div>

          <div className="grid gap-2">
            <div className="flex items-center justify-between">
              <Label>Requirements (JSON) <span className="text-destructive">*</span></Label>
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
                    {ex.label.split(" ")[0]}
                  </Button>
                ))}
              </div>
            </div>
            <Textarea
              value={data.requirements}
              onChange={(e) => update("requirements", e.target.value)}
              rows={3}
              placeholder='{"attempts_count": 10}'
              className={`font-mono text-sm ${errors.requirements ? "border-destructive" : ""}`}
            />
            {errors.requirements && <p className="text-sm text-destructive">{errors.requirements}</p>}
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_secret"
              checked={data.is_secret}
              onChange={(e) => update("is_secret", e.target.checked)}
              className="rounded"
            />
            <Label htmlFor="is_secret">Badge secret</Label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Annuler
          </Button>
          <Button onClick={handleCreate} disabled={saving}>
            {saving ? "Création..." : "Créer"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
