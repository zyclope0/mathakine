"use client";

import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
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
import { BADGE_CATEGORIES, BADGE_DIFFICULTIES } from "@/lib/constants/badges";

const REQUIREMENT_EXAMPLE_VALUES = [
  '{"attempts_count": 10}',
  '{"min_attempts": 50, "success_rate": 80}',
  '{"consecutive_days": 7}',
  '{"max_time": 5}',
  '{"logic_attempts_count": 10}',
  '{"attempts_count": 20, "logic_attempts_count": 5}',
  '{"comeback_days": 7}',
] as const;

const REQUIREMENT_EXAMPLE_KEYS = [
  "attempts",
  "successRate",
  "consecutiveDays",
  "maxTime",
  "logicChallenges",
  "mixed",
  "comeback",
] as const;

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

export function BadgeCreateModal({ open, onOpenChange, onCreated }: BadgeCreateModalProps) {
  const t = useTranslations("adminPages.content.badgeCreateModal");
  const [data, setData] = useState(initialState);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [principlesOpen, setPrinciplesOpen] = useState(false);

  const requirementExamples = useMemo(
    () =>
      REQUIREMENT_EXAMPLE_KEYS.map((key, i) => ({
        value: REQUIREMENT_EXAMPLE_VALUES[i],
        short: t(`examples.${key}.short`),
        label: t(`examples.${key}.label`),
      })),
    [t]
  );

  const update = (k: keyof typeof initialState, v: unknown) => {
    setData((prev) => ({ ...prev, [k]: v }));
    if (errors[k as string]) setErrors((prev) => ({ ...prev, [k]: "" }));
  };

  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!data.code.trim()) e.code = t("validation.codeRequired");
    else if (!/^[a-z0-9_]+$/.test(data.code.replace(/\s/g, "_")))
      e.code = t("validation.codeInvalid");
    if (!data.name.trim()) e.name = t("validation.nameRequired");
    try {
      const req = JSON.parse(data.requirements || "{}");
      if (!req || typeof req !== "object" || Object.keys(req).length === 0)
        e.requirements = t("validation.requirementsInvalidSchema");
    } catch {
      e.requirements = t("validation.requirementsInvalidJson");
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleCreate = async () => {
    if (!validate()) {
      toast.error(t("toasts.incompleteFields"), {
        description: t("toasts.incompleteFieldsDescription"),
      });
      return;
    }
    setSaving(true);
    try {
      let requirements: Record<string, unknown>;
      try {
        requirements = JSON.parse(data.requirements) as Record<string, unknown>;
      } catch {
        toast.error(t("toasts.requirementsJsonInvalid"));
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
      toast.success(t("toasts.badgeCreated"));
      setData(initialState);
      onOpenChange(false);
      onCreated();
    } catch (err) {
      const msg = err instanceof Error ? err.message : t("toasts.createFailed");
      toast.error(t("toasts.errorTitle"), { description: msg });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t("title")}</DialogTitle>
        </DialogHeader>

        <div className="mb-4">
          <Button
            variant="outline"
            size="sm"
            className="w-full justify-between"
            onClick={() => setPrinciplesOpen(!principlesOpen)}
          >
            <span className="flex items-center gap-2">
              <Info className="h-4 w-4" aria-hidden="true" />
              {t("principlesToggle")}
            </span>
            {principlesOpen ? (
              <ChevronUp className="h-4 w-4" aria-hidden="true" />
            ) : (
              <ChevronDown className="h-4 w-4" aria-hidden="true" />
            )}
          </Button>
          {principlesOpen && (
            <div className="mt-2 space-y-1.5 rounded-md border bg-muted/50 p-3 text-sm">
              <p>
                <strong>{t("principles.goalGradientBold")}</strong>{" "}
                {t("principles.goalGradientBody")}
              </p>
              <p>
                <strong>{t("principles.endowmentBold")}</strong> {t("principles.endowmentBody")}
              </p>
              <p>
                <strong>{t("principles.scarcityBold")}</strong> {t("principles.scarcityBody")}
              </p>
              <p>
                <strong>{t("principles.socialProofBold")}</strong> {t("principles.socialProofBody")}
              </p>
              <p>
                <strong>{t("principles.lossAversionBold")}</strong>{" "}
                {t("principles.lossAversionBody")}
              </p>
              <p className="mt-2 border-t border-border/50 pt-2">
                <strong>{t("principles.visualBold")}</strong> {t("principles.visualBody")}
              </p>
            </div>
          )}
        </div>

        <div className="grid gap-4 py-2">
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label>
                {t("labels.code")} <span className="text-destructive">*</span>
              </Label>
              <Input
                value={data.code}
                onChange={(e) => update("code", e.target.value)}
                placeholder={t("placeholders.code")}
                className={errors.code ? "border-destructive" : ""}
              />
              {errors.code && <p className="text-sm text-destructive">{errors.code}</p>}
            </div>
            <div className="grid gap-2">
              <Label>
                {t("labels.name")} <span className="text-destructive">*</span>
              </Label>
              <Input
                value={data.name}
                onChange={(e) => update("name", e.target.value)}
                placeholder={t("placeholders.name")}
                className={errors.name ? "border-destructive" : ""}
              />
              {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
            </div>
          </div>

          <div className="grid gap-2">
            <Label>{t("labels.description")}</Label>
            <Textarea
              value={data.description}
              onChange={(e) => update("description", e.target.value)}
              rows={2}
              placeholder={t("placeholders.description")}
            />
          </div>

          <div className="grid gap-2">
            <Label>{t("labels.icon")}</Label>
            <Input
              value={data.icon_url}
              onChange={(e) => update("icon_url", e.target.value)}
              placeholder={t("placeholders.icon")}
            />
            <p className="text-xs text-muted-foreground">{t("hints.iconHelp")}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label>{t("labels.category")}</Label>
              <Select value={data.category} onValueChange={(v) => update("category", v)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {BADGE_CATEGORIES.map((c) => (
                    <SelectItem key={c} value={c}>
                      {t(`categoryOptions.${c}`)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>{t("labels.difficulty")}</Label>
              <Select value={data.difficulty} onValueChange={(v) => update("difficulty", v)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {BADGE_DIFFICULTIES.map((d) => (
                    <SelectItem key={d} value={d}>
                      {t(`difficultyOptions.${d}`)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label>{t("labels.points")}</Label>
              <Input
                type="number"
                min={0}
                value={data.points_reward}
                onChange={(e) => update("points_reward", e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label>{t("labels.thematicTitle")}</Label>
              <Input
                value={data.star_wars_title}
                onChange={(e) => update("star_wars_title", e.target.value)}
                placeholder={t("placeholders.thematicTitle")}
              />
            </div>
          </div>

          <div className="grid gap-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <Label>
                {t("labels.requirementsJson")} <span className="text-destructive">*</span>
              </Label>
              <div className="flex flex-wrap gap-1">
                {requirementExamples.map((ex) => (
                  <Button
                    key={ex.value}
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-7 text-xs"
                    title={ex.label}
                    aria-label={ex.label}
                    onClick={() => update("requirements", ex.value)}
                  >
                    {ex.short}
                  </Button>
                ))}
              </div>
            </div>
            <Textarea
              value={data.requirements}
              onChange={(e) => update("requirements", e.target.value)}
              rows={3}
              placeholder={t("placeholders.requirements")}
              className={`font-mono text-sm ${errors.requirements ? "border-destructive" : ""}`}
            />
            {errors.requirements && (
              <p className="text-sm text-destructive">{errors.requirements}</p>
            )}
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_secret"
              checked={data.is_secret}
              onChange={(e) => update("is_secret", e.target.checked)}
              className="rounded"
            />
            <Label htmlFor="is_secret">{t("labels.secretBadge")}</Label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("cancel")}
          </Button>
          <Button onClick={handleCreate} disabled={saving}>
            {saving ? t("creating") : t("create")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
