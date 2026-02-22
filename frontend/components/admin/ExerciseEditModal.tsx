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
import { Copy, Plus, Trash2 } from "lucide-react";

export interface ExerciseDetail {
  id: number;
  title: string;
  exercise_type: string;
  difficulty: string;
  age_group: string;
  question: string;
  correct_answer: string;
  choices: string[] | null;
  explanation: string;
  hint: string;
  is_archived: boolean;
  [key: string]: unknown;
}

const EXERCISE_TYPES = [
  "ADDITION",
  "SOUSTRACTION",
  "MULTIPLICATION",
  "DIVISION",
  "FRACTIONS",
  "GEOMETRIE",
  "TEXTE",
  "MIXTE",
  "DIVERS",
];

const DIFFICULTIES = ["INITIE", "PADAWAN", "CHEVALIER", "MAITRE", "GRAND_MAITRE"];

interface ExerciseEditModalProps {
  exerciseId: number | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
}

export function ExerciseEditModal({
  exerciseId,
  open,
  onOpenChange,
  onSaved,
}: ExerciseEditModalProps) {
  const [data, setData] = useState<ExerciseDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [duplicating, setDuplicating] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!open || !exerciseId) return;
    setErrors({});
    setLoading(true);
    api
      .get<ExerciseDetail>(`/api/admin/exercises/${exerciseId}`)
      .then((res) => setData(res))
      .catch(() => toast.error("Erreur de chargement"))
      .finally(() => setLoading(false));
  }, [open, exerciseId]);

  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!data?.title?.trim()) e.title = "Le titre est obligatoire";
    if (!data?.question?.trim()) e.question = "La question est obligatoire";
    if (!data?.correct_answer?.trim()) e.correct_answer = "La réponse correcte est obligatoire";
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
      await api.put(`/api/admin/exercises/${data.id}`, {
        title: data.title,
        exercise_type: data.exercise_type,
        difficulty: data.difficulty,
        age_group: data.age_group,
        question: data.question,
        correct_answer: data.correct_answer,
        choices: data.choices,
        explanation: data.explanation || "",
        hint: data.hint || "",
        is_archived: data.is_archived,
      });
      toast.success("Exercice mis à jour");
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

  const update = (k: keyof ExerciseDetail, v: unknown) => {
    if (!data) return;
    setData({ ...data, [k]: v });
    if (errors[k]) setErrors((prev) => ({ ...prev, [k]: "" }));
  };

  const choicesList: string[] = Array.isArray(data?.choices) ? [...data.choices] : [];

  const addChoice = () => {
    if (!data) return;
    const current = Array.isArray(data.choices) ? data.choices : [];
    update("choices", [...current, ""]);
  };

  const updateChoice = (idx: number, val: string) => {
    if (!data) return;
    const current = Array.isArray(data.choices) ? [...data.choices] : [];
    current[idx] = val;
    update("choices", current);
  };

  const removeChoice = (idx: number) => {
    if (!data) return;
    const current = Array.isArray(data.choices) ? [...data.choices] : [];
    current.splice(idx, 1);
    update("choices", current.length ? current : null);
  };

  const handleDuplicate = async () => {
    if (!data) return;
    setDuplicating(true);
    try {
      const copy = await api.post<ExerciseDetail>(`/api/admin/exercises/${data.id}/duplicate`, {});
      toast.success("Exercice dupliqué", { description: `Créé : ${copy.title}` });
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
          <DialogTitle>Éditer l&apos;exercice</DialogTitle>
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
                placeholder="Titre de l'exercice"
                className={errors.title ? "border-destructive" : ""}
              />
              {errors.title && <p className="text-sm text-destructive">{errors.title}</p>}
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="grid gap-2">
                <Label>Type</Label>
                <Select
                  value={data.exercise_type}
                  onValueChange={(v) => update("exercise_type", v)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {EXERCISE_TYPES.map((t) => (
                      <SelectItem key={t} value={t}>
                        {t}
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
              <div className="grid gap-2">
                <Label>Âge</Label>
                <Input
                  value={data.age_group}
                  onChange={(e) => update("age_group", e.target.value)}
                  placeholder="ex: 8-10"
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label>
                Question / Énoncé <span className="text-destructive">*</span>
              </Label>
              <Textarea
                value={data.question}
                onChange={(e) => update("question", e.target.value)}
                rows={4}
                placeholder="Énoncé de l'exercice"
                className={errors.question ? "border-destructive" : ""}
              />
              {errors.question && <p className="text-sm text-destructive">{errors.question}</p>}
            </div>
            <div className="grid gap-2">
              <Label>
                Réponse correcte <span className="text-destructive">*</span>
              </Label>
              <Input
                value={data.correct_answer}
                onChange={(e) => update("correct_answer", e.target.value)}
                placeholder="Réponse attendue"
                className={errors.correct_answer ? "border-destructive" : ""}
              />
              {errors.correct_answer && (
                <p className="text-sm text-destructive">{errors.correct_answer}</p>
              )}
            </div>
            <div className="grid gap-2">
              <div className="flex items-center justify-between">
                <Label>Choix multiples (QCM)</Label>
                <Button type="button" variant="outline" size="sm" onClick={addChoice}>
                  <Plus className="h-4 w-4 mr-1" /> Ajouter une option
                </Button>
              </div>
              {choicesList.length > 0 && (
                <div className="space-y-2 rounded-md border p-3">
                  {choicesList.map((opt, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <input
                        type="radio"
                        name="correct-choice"
                        checked={data.correct_answer === opt}
                        onChange={() => update("correct_answer", opt)}
                        aria-label={`Option ${idx + 1} est la bonne réponse`}
                      />
                      <Input
                        value={opt}
                        onChange={(e) => updateChoice(idx, e.target.value)}
                        placeholder={`Option ${idx + 1}`}
                        className="flex-1"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeChoice(idx)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="grid gap-2">
              <Label>Explication</Label>
              <Textarea
                value={data.explanation || ""}
                onChange={(e) => update("explanation", e.target.value)}
                rows={2}
                placeholder="Explication de la solution"
              />
            </div>
            <div className="grid gap-2">
              <Label>Indice</Label>
              <Input
                value={data.hint || ""}
                onChange={(e) => update("hint", e.target.value)}
                placeholder="Indice pour l'apprenant"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="ex-archived"
                checked={data.is_archived}
                onChange={(e) => update("is_archived", e.target.checked)}
                className="h-4 w-4 rounded border"
                aria-label="Exercice archivé"
              />
              <Label htmlFor="ex-archived">Archivé</Label>
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
