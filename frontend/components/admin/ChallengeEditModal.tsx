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
import { toast } from "sonner";
import { api } from "@/lib/api/client";
import { ChevronDown, ChevronRight, Copy, Plus, Trash2 } from "lucide-react";

export interface ChallengeDetail {
  id: number;
  title: string;
  description: string;
  challenge_type: string;
  age_group: string;
  difficulty: string;
  content: string;
  question: string;
  solution: string;
  correct_answer: string;
  choices: string[] | null;
  solution_explanation: string;
  visual_data: Record<string, unknown> | null;
  hints: string[] | null;
  is_archived: boolean;
  [key: string]: unknown;
}

const CHALLENGE_TYPES = [
  { value: "sequence", label: "Suite logique" },
  { value: "pattern", label: "Motif" },
  { value: "visual", label: "Visuel" },
  { value: "puzzle", label: "Puzzle" },
  { value: "riddle", label: "Énigme" },
  { value: "deduction", label: "Déduction" },
  { value: "probability", label: "Probabilité" },
  { value: "graph", label: "Graphe" },
  { value: "coding", label: "Codage" },
  { value: "chess", label: "Échecs" },
  { value: "custom", label: "Personnalisé" },
];

const AGE_GROUPS = [
  { value: "GROUP_6_8", label: "6-8 ans" },
  { value: "GROUP_10_12", label: "9-11 ans" },
  { value: "GROUP_13_15", label: "12-14 ans" },
  { value: "GROUP_15_17", label: "15-17 ans" },
  { value: "ADULT", label: "Adulte" },
  { value: "ALL_AGES", label: "Tous âges" },
];

interface ChallengeEditModalProps {
  challengeId: number | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
}

export function ChallengeEditModal({
  challengeId,
  open,
  onOpenChange,
  onSaved,
}: ChallengeEditModalProps) {
  const [data, setData] = useState<ChallengeDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [duplicating, setDuplicating] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!open || !challengeId) return;
    setErrors({});
    setLoading(true);
    api
      .get<ChallengeDetail>(`/api/admin/challenges/${challengeId}`)
      .then((res) => setData(res))
      .catch(() => toast.error("Erreur de chargement"))
      .finally(() => setLoading(false));
  }, [open, challengeId]);

  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!data?.title?.trim()) e.title = "Le titre est obligatoire";
    if (!data?.description?.trim()) e.description = "La description est obligatoire";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSave = async () => {
    if (!data) return;
    let visualDataToSend: Record<string, unknown> | null = null;
    const trimmed = visualDataRaw.trim();
    if (trimmed) {
      try {
        visualDataToSend = JSON.parse(trimmed) as Record<string, unknown>;
      } catch {
        toast.error("visual_data : JSON invalide");
        return;
      }
    }
    if (!validate()) {
      toast.error("Champs incomplets", { description: "Vérifiez les champs obligatoires." });
      return;
    }
    setSaving(true);
    try {
      await api.put(`/api/admin/challenges/${data.id}`, {
        title: data.title,
        description: data.description,
        challenge_type: data.challenge_type,
        age_group: data.age_group,
        difficulty: data.difficulty || "",
        content: data.content || "",
        question: data.question || "",
        solution: data.solution || "",
        correct_answer: data.correct_answer || "",
        choices: data.choices,
        solution_explanation: data.solution_explanation || "",
        visual_data: visualDataToSend,
        hints: data.hints,
        is_archived: data.is_archived,
      });
      toast.success("Défi mis à jour");
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

  const update = (k: keyof ChallengeDetail, v: unknown) => {
    if (!data) return;
    setData({ ...data, [k]: v });
    if (errors[k]) setErrors((prev) => ({ ...prev, [k]: "" }));
  };

  const [visualDataRaw, setVisualDataRaw] = useState("");
  const [visualDataExpanded, setVisualDataExpanded] = useState(false);
  useEffect(() => {
    if (data?.visual_data != null && typeof data.visual_data === "object") {
      try {
        setVisualDataRaw(JSON.stringify(data.visual_data, null, 2));
      } catch {
        setVisualDataRaw("{}");
      }
    } else {
      setVisualDataRaw("");
    }
  }, [data?.id, data?.visual_data]);

  const hintsList: string[] = Array.isArray(data?.hints) ? [...data.hints] : [];

  const addHint = () => {
    if (!data) return;
    const current = Array.isArray(data.hints) ? data.hints : [];
    update("hints", [...current, ""]);
  };

  const updateHint = (idx: number, val: string) => {
    if (!data) return;
    const current = Array.isArray(data.hints) ? [...data.hints] : [];
    current[idx] = val;
    update("hints", current);
  };

  const removeHint = (idx: number) => {
    if (!data) return;
    const current = Array.isArray(data.hints) ? [...data.hints] : [];
    current.splice(idx, 1);
    update("hints", current.length ? current : null);
  };

  const handleDuplicate = async () => {
    if (!data) return;
    setDuplicating(true);
    try {
      const copy = await api.post<ChallengeDetail>(
        `/api/admin/challenges/${data.id}/duplicate`,
        {}
      );
      toast.success("Défi dupliqué", { description: `Créé : ${copy.title}` });
      onOpenChange(false);
      onSaved();
    } catch (err) {
      toast.error("Erreur", {
        description: err instanceof Error ? err.message : "Échec de la duplication",
      });
    } finally {
      setDuplicating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Éditer le défi</DialogTitle>
        </DialogHeader>
        {loading ? (
          <p className="py-8 text-center text-muted-foreground">Chargement...</p>
        ) : data ? (
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>
                Titre <span className="text-destructive">*</span>
              </Label>
              <Input
                value={data.title}
                onChange={(e) => update("title", e.target.value)}
                placeholder="Titre du défi"
                className={errors.title ? "border-destructive" : ""}
              />
              {errors.title && <p className="text-sm text-destructive">{errors.title}</p>}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Type</Label>
                <Select
                  value={data.challenge_type}
                  onValueChange={(v) => update("challenge_type", v)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CHALLENGE_TYPES.map((t) => (
                      <SelectItem key={t.value} value={t.value}>
                        {t.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label>Groupe d&apos;âge</Label>
                <Select value={data.age_group} onValueChange={(v) => update("age_group", v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {AGE_GROUPS.map((a) => (
                      <SelectItem key={a.value} value={a.value}>
                        {a.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid gap-2">
              <Label>
                Description <span className="text-destructive">*</span>
              </Label>
              <Textarea
                value={data.description}
                onChange={(e) => update("description", e.target.value)}
                rows={3}
                placeholder="Description du défi"
                className={errors.description ? "border-destructive" : ""}
              />
              {errors.description && (
                <p className="text-sm text-destructive">{errors.description}</p>
              )}
            </div>
            <div className="grid gap-2">
              <Label>Consigne / Question</Label>
              <Textarea
                value={data.question || data.content || ""}
                onChange={(e) => {
                  update("question", e.target.value);
                  update("content", e.target.value);
                }}
                rows={4}
                placeholder="Consigne ou question"
              />
            </div>
            <div className="grid gap-2">
              <Label>Solution / Réponse correcte</Label>
              <Input
                value={data.correct_answer || data.solution || ""}
                onChange={(e) => {
                  update("correct_answer", e.target.value);
                  update("solution", e.target.value);
                }}
                placeholder="Réponse attendue"
              />
            </div>
            <div className="grid gap-2">
              <Label>Explication de la solution</Label>
              <Textarea
                value={data.solution_explanation || ""}
                onChange={(e) => update("solution_explanation", e.target.value)}
                rows={2}
                placeholder="Explication détaillée"
              />
            </div>
            <div className="grid gap-2">
              <Label>Indices (pistes pédagogiques)</Label>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Guident sans donner la réponse
                </span>
                <Button type="button" variant="outline" size="sm" onClick={addHint}>
                  <Plus className="h-4 w-4 mr-1" /> Ajouter un indice
                </Button>
              </div>
              {hintsList.length > 0 && (
                <div className="space-y-2 rounded-md border p-3">
                  {hintsList.map((hint, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <span className="text-sm text-muted-foreground w-6">{idx + 1}.</span>
                      <Input
                        value={hint}
                        onChange={(e) => updateHint(idx, e.target.value)}
                        placeholder={`Indice ${idx + 1}`}
                        className="flex-1"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeHint(idx)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="grid gap-2">
              <button
                type="button"
                onClick={() => setVisualDataExpanded((v) => !v)}
                className="flex items-center gap-2 text-left font-medium hover:underline"
              >
                {visualDataExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
                <Label className="cursor-pointer">Visual data (JSON)</Label>
              </button>
              {visualDataExpanded && (
                <>
                  <p className="text-xs text-muted-foreground">
                    Structure selon le type (sequence, pattern, puzzle, deduction, etc.). Voir la
                    doc des prompts IA.
                  </p>
                  <Textarea
                    value={visualDataRaw}
                    onChange={(e) => setVisualDataRaw(e.target.value)}
                    rows={8}
                    placeholder='{"sequence": [2, 4, 6, 8], "pattern": "n+2"}'
                    className="font-mono text-sm"
                  />
                </>
              )}
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="ch-archived"
                checked={data.is_archived}
                onChange={(e) => update("is_archived", e.target.checked)}
                className="h-4 w-4 rounded border"
                aria-label="Défi archivé"
              />
              <Label htmlFor="ch-archived">Archivé</Label>
            </div>
          </div>
        ) : null}
        <DialogFooter className="flex-col gap-2 sm:flex-row sm:justify-between">
          <Button
            variant="outline"
            size="sm"
            onClick={handleDuplicate}
            disabled={duplicating || !data}
          >
            <Copy className="h-4 w-4 mr-1" />
            {duplicating ? "Duplication..." : "Dupliquer"}
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Annuler
            </Button>
            <Button onClick={handleSave} disabled={saving || !data}>
              {saving ? "Enregistrement..." : "Enregistrer"}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
