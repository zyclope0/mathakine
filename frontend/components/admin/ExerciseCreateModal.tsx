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
import { toast } from "sonner";
import { api } from "@/lib/api/client";

const EXERCISE_TYPES = [
  "ADDITION", "SOUSTRACTION", "MULTIPLICATION", "DIVISION",
  "FRACTIONS", "GEOMETRIE", "TEXTE", "MIXTE", "DIVERS",
];

const DIFFICULTIES = ["INITIE", "PADAWAN", "CHEVALIER", "MAITRE", "GRAND_MAITRE"];

const AGE_GROUPS = [
  { value: "6-8", label: "6-8 ans" },
  { value: "9-11", label: "9-11 ans" },
  { value: "12-14", label: "12-14 ans" },
  { value: "15-17", label: "15-17 ans" },
  { value: "adulte", label: "Adulte" },
];

interface ExerciseCreateModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}

const initialState = {
  title: "",
  exercise_type: "ADDITION",
  difficulty: "PADAWAN",
  age_group: "9-11",
  question: "",
  correct_answer: "",
  choices: null as string[] | null,
  explanation: "",
  hint: "",
};

export function ExerciseCreateModal({
  open,
  onOpenChange,
  onCreated,
}: ExerciseCreateModalProps) {
  const [data, setData] = useState(initialState);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const update = (k: keyof typeof initialState, v: unknown) => {
    setData((prev) => ({ ...prev, [k]: v }));
    if (errors[k]) setErrors((prev) => ({ ...prev, [k]: "" }));
  };

  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!data.title.trim()) e.title = "Le titre est obligatoire";
    if (!data.question.trim()) e.question = "La question est obligatoire";
    if (!data.correct_answer.trim()) e.correct_answer = "La réponse correcte est obligatoire";
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
      await api.post("/api/admin/exercises", {
        title: data.title,
        exercise_type: data.exercise_type,
        difficulty: data.difficulty,
        age_group: data.age_group,
        question: data.question,
        correct_answer: data.correct_answer,
        choices: data.choices,
        explanation: data.explanation || undefined,
        hint: data.hint || undefined,
      });
      toast.success("Exercice créé");
      setData(initialState);
      onOpenChange(false);
      onCreated();
    } catch (err) {
      toast.error("Erreur", { description: err instanceof Error ? err.message : "Échec de la création" });
    } finally {
      setSaving(false);
    }
  };

  const addChoice = () => {
    const current = data.choices || [];
    update("choices", [...current, ""]);
  };

  const updateChoice = (idx: number, val: string) => {
    const current = data.choices || [];
    const next = [...current];
    next[idx] = val;
    update("choices", next);
  };

  const removeChoice = (idx: number) => {
    const current = data.choices || [];
    const next = current.filter((_, i) => i !== idx);
    update("choices", next.length ? next : null);
  };

  const choicesList = data.choices || [];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Créer un exercice</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Titre <span className="text-destructive">*</span></Label>
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
              <Select value={data.exercise_type} onValueChange={(v) => update("exercise_type", v)}>
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
            <Label>Question / Énoncé <span className="text-destructive">*</span></Label>
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
            <Label>Réponse correcte <span className="text-destructive">*</span></Label>
            <Input
              value={data.correct_answer}
              onChange={(e) => update("correct_answer", e.target.value)}
              placeholder="Réponse attendue"
              className={errors.correct_answer ? "border-destructive" : ""}
            />
            {errors.correct_answer && <p className="text-sm text-destructive">{errors.correct_answer}</p>}
          </div>
          <div className="grid gap-2">
            <div className="flex items-center justify-between">
              <Label>Choix multiples (QCM)</Label>
              <Button type="button" variant="outline" size="sm" onClick={addChoice}>
                Ajouter une option
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
                    <Button type="button" variant="ghost" size="sm" onClick={() => removeChoice(idx)}>
                      Supprimer
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="grid gap-2">
            <Label>Explication</Label>
            <Textarea
              value={data.explanation}
              onChange={(e) => update("explanation", e.target.value)}
              rows={2}
              placeholder="Explication de la solution"
            />
          </div>
          <div className="grid gap-2">
            <Label>Indice</Label>
            <Input
              value={data.hint}
              onChange={(e) => update("hint", e.target.value)}
              placeholder="Indice pour l'apprenant"
            />
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
