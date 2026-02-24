"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Loader2, Sparkles } from "lucide-react";
import { useTranslations } from "next-intl";
import { api } from "@/lib/api/client";
import { useQueryClient } from "@tanstack/react-query";
import { AGE_GROUPS, getAgeGroupDisplay } from "@/lib/constants/exercises";

const LEARNING_GOALS = ["reviser", "preparer_exam", "progresser", "samuser", "autre"] as const;
const PRACTICE_RHYTHMS = [
  "10min_jour",
  "20min_jour",
  "30min_semaine",
  "1h_semaine",
  "flexible",
] as const;

const GRADE_SYSTEMS = ["suisse", "unifie"] as const;

function OnboardingContent() {
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const t = useTranslations("onboarding");

  const [gradeSystem, setGradeSystem] = useState<"suisse" | "unifie">(
    (user?.grade_system as "suisse" | "unifie") || "unifie"
  );
  const [gradeLevel, setGradeLevel] = useState(user?.grade_level?.toString() || "");
  const [ageGroup, setAgeGroup] = useState(user?.preferred_difficulty || "");
  const [learningGoal, setLearningGoal] = useState(user?.learning_goal || "");
  const [practiceRhythm, setPracticeRhythm] = useState(user?.practice_rhythm || "");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const maxGrade = gradeSystem === "suisse" ? 11 : 12;
  const gradeOptions = Array.from({ length: maxGrade }, (_, i) => i + 1);

  const handleGradeSystemChange = (v: string) => {
    const next = v as "suisse" | "unifie";
    setGradeSystem(next);
    const max = next === "suisse" ? 11 : 12;
    if (gradeLevel && parseInt(gradeLevel, 10) > max) {
      setGradeLevel("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!gradeLevel) {
      setError("Sélectionne ta classe.");
      return;
    }
    setIsSubmitting(true);
    try {
      await api.put("/api/users/me", {
        grade_level: parseInt(gradeLevel, 10),
        grade_system: gradeSystem,
        preferred_difficulty: ageGroup || undefined,
        learning_goal: learningGoal || undefined,
        practice_rhythm: practiceRhythm || undefined,
      });
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
      router.replace("/dashboard");
    } catch (err: unknown) {
      setError(
        err && typeof err === "object" && "message" in err
          ? (err as { message: string }).message
          : "Erreur lors de l'enregistrement"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const tGoal = (key: (typeof LEARNING_GOALS)[number]) => t(`goals.${String(key)}`);
  const tRhythm = (key: (typeof PRACTICE_RHYTHMS)[number]) => t(`rhythms.${String(key)}`);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <Sparkles className="h-12 w-12 text-primary" />
          </div>
          <CardTitle className="text-2xl font-bold">{t("title")}</CardTitle>
          <CardDescription>{t("description")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="grade_system">{t("gradeSystem")}</Label>
              <Select
                value={gradeSystem}
                onValueChange={handleGradeSystemChange}
                disabled={isSubmitting}
              >
                <SelectTrigger id="grade_system">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {GRADE_SYSTEMS.map((sys) => (
                    <SelectItem key={sys} value={sys}>
                      {t(`gradeSystems.${sys}`)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="grade_level">{t("gradeLevel")} *</Label>
              <Select
                value={gradeLevel}
                onValueChange={setGradeLevel}
                disabled={isSubmitting}
                required
              >
                <SelectTrigger id="grade_level">
                  <SelectValue placeholder={t("gradeLevelPlaceholder")} />
                </SelectTrigger>
                <SelectContent>
                  {gradeOptions.map((level) => (
                    <SelectItem key={level} value={level.toString()}>
                      {gradeSystem === "suisse" ? `${level}H` : level}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="age_group">{t("ageGroup")}</Label>
              <Select value={ageGroup} onValueChange={setAgeGroup} disabled={isSubmitting}>
                <SelectTrigger id="age_group">
                  <SelectValue placeholder={t("ageGroupPlaceholder")} />
                </SelectTrigger>
                <SelectContent>
                  {Object.values(AGE_GROUPS)
                    .filter((g) => g !== AGE_GROUPS.ALL_AGES)
                    .map((group) => (
                      <SelectItem key={group} value={group}>
                        {getAgeGroupDisplay(group)}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="learning_goal">{t("learningGoal")}</Label>
              <Select
                value={learningGoal || "none"}
                onValueChange={(v) => setLearningGoal(v === "none" ? "" : v)}
                disabled={isSubmitting}
              >
                <SelectTrigger id="learning_goal">
                  <SelectValue placeholder={t("learningGoalPlaceholder")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">—</SelectItem>
                  {LEARNING_GOALS.map((g) => (
                    <SelectItem key={g} value={g}>
                      {tGoal(g)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="practice_rhythm">{t("practiceRhythm")}</Label>
              <Select
                value={practiceRhythm || "none"}
                onValueChange={(v) => setPracticeRhythm(v === "none" ? "" : v)}
                disabled={isSubmitting}
              >
                <SelectTrigger id="practice_rhythm">
                  <SelectValue placeholder={t("practiceRhythmPlaceholder")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">—</SelectItem>
                  {PRACTICE_RHYTHMS.map((r) => (
                    <SelectItem key={r} value={r}>
                      {tRhythm(r)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {error && (
              <p className="text-sm text-destructive" role="alert">
                {error}
              </p>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting}
              aria-busy={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t("submitting")}
                </>
              ) : (
                t("submit")
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default function OnboardingPage() {
  return (
    <ProtectedRoute>
      <OnboardingContent />
    </ProtectedRoute>
  );
}
