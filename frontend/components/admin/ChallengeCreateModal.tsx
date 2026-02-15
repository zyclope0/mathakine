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

interface ChallengeCreateModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}

const initialState = {
  title: "",
  description: "",
  challenge_type: "puzzle",
  age_group: "GROUP_10_12",
  question: "",
  correct_answer: "",
  solution_explanation: "",
  visual_data: "" as string,
};

export function ChallengeCreateModal({
  open,
  onOpenChange,
  onCreated,
}: ChallengeCreateModalProps) {
  const [data, setData] = useState(initialState);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const update = (k: keyof typeof initialState, v: string) => {
    setData((prev) => ({ ...prev, [k]: v }));
    if (errors[k]) setErrors((prev) => ({ ...prev, [k]: "" }));
  };

  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!data.title.trim()) e.title = "Le titre est obligatoire";
    if (!data.description.trim()) e.description = "La description est obligatoire";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleCreate = async () => {
    let visualDataObj: Record<string, unknown> | null = null;
    if (data.visual_data.trim()) {
      try {
        visualDataObj = JSON.parse(data.visual_data) as Record<string, unknown>;
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
      await api.post("/api/admin/challenges", {
        title: data.title,
        description: data.description,
        challenge_type: data.challenge_type,
        age_group: data.age_group,
        question: data.question || undefined,
        correct_answer: data.correct_answer || undefined,
        solution_explanation: data.solution_explanation || undefined,
        visual_data: visualDataObj,
      });
      toast.success("Défi créé");
      setData(initialState);
      onOpenChange(false);
      onCreated();
    } catch (err) {
      toast.error("Erreur", { description: err instanceof Error ? err.message : "Échec de la création" });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Créer un défi</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Titre <span className="text-destructive">*</span></Label>
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
              <Select value={data.challenge_type} onValueChange={(v) => update("challenge_type", v)}>
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
            <Label>Description <span className="text-destructive">*</span></Label>
            <Textarea
              value={data.description}
              onChange={(e) => update("description", e.target.value)}
              rows={3}
              placeholder="Description du défi"
              className={errors.description ? "border-destructive" : ""}
            />
            {errors.description && <p className="text-sm text-destructive">{errors.description}</p>}
          </div>
          <div className="grid gap-2">
            <Label>Consigne / Question</Label>
            <Textarea
              value={data.question}
              onChange={(e) => update("question", e.target.value)}
              rows={4}
              placeholder="Consigne ou question"
            />
          </div>
          <div className="grid gap-2">
            <Label>Solution / Réponse correcte</Label>
            <Input
              value={data.correct_answer}
              onChange={(e) => update("correct_answer", e.target.value)}
              placeholder="Réponse attendue"
            />
          </div>
          <div className="grid gap-2">
            <Label>Explication de la solution</Label>
            <Textarea
              value={data.solution_explanation}
              onChange={(e) => update("solution_explanation", e.target.value)}
              rows={2}
              placeholder="Explication détaillée"
            />
          </div>
          <div className="grid gap-2">
            <Label>Visual data (JSON)</Label>
            <Textarea
              value={data.visual_data}
              onChange={(e) => update("visual_data", e.target.value)}
              rows={4}
              placeholder='{"sequence": [2, 4, 6, 8], "pattern": "n+2"}'
              className="font-mono text-sm"
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
