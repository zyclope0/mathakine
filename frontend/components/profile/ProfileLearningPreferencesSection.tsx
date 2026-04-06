"use client";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Settings, Save, X, Loader2, Pencil } from "lucide-react";
import { useTranslations } from "next-intl";
import { AGE_GROUPS, type AgeGroup } from "@/lib/constants/exercises";
import {
  USER_PROFILE_AGE_GROUPS,
  type UserProfileAgeGroup,
} from "@/lib/constants/userProfileAgeGroup";
import {
  GRADE_SYSTEMS,
  LEARNING_GOALS,
  PRACTICE_RHYTHMS,
  type GradeSystem,
} from "@/lib/profile/profilePage";
import type { LearningPrefsState } from "@/hooks/useProfilePageController";

interface ProfileLearningPreferencesSectionProps {
  user: {
    grade_system?: string | null;
    grade_level?: number | null;
    age_group?: string | null;
    learning_style?: string | null;
    preferred_difficulty?: string | null;
    learning_goal?: string | null;
    practice_rhythm?: string | null;
  };
  isEditing: boolean;
  learningPrefs: LearningPrefsState;
  isUpdatingProfile: boolean;
  getAgeDisplay: (group: string) => string;
  onStartEditing: () => void;
  onLearningPrefsChange: (update: Partial<LearningPrefsState>) => void;
  onSave: () => void;
  onCancel: () => void;
}

/**
 * Section préférences d'apprentissage (lecture + édition).
 * Composant purement visuel + callbacks.
 *
 * FFI-L11.
 */
export function ProfileLearningPreferencesSection({
  user,
  isEditing,
  learningPrefs,
  isUpdatingProfile,
  getAgeDisplay,
  onStartEditing,
  onLearningPrefsChange,
  onSave,
  onCancel,
}: ProfileLearningPreferencesSectionProps) {
  const t = useTranslations("profile");
  const tLearning = useTranslations("profile.learningPreferences");
  const tOnboarding = useTranslations("onboarding");
  const tActions = useTranslations("profile.actions");

  return (
    <div className="animate-fade-in-up-delay-1">
      <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
        <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-xl">
              <Settings className="h-5 w-5 text-primary" />
              {tLearning("title")}
            </CardTitle>
            {!isEditing && (
              <Button
                variant="outline"
                size="sm"
                onClick={onStartEditing}
                aria-label={tActions("edit")}
                className="inline-flex items-center gap-2 border-border hover:bg-accent hover:text-accent-foreground rounded-lg h-9 px-3"
              >
                <Pencil className="h-3.5 w-3.5" />
                {tActions("edit")}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {isEditing ? (
            <div className="flex flex-col">
              {/* Système de notation */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <Label htmlFor="grade_system" className="text-sm font-medium text-foreground">
                    {tOnboarding("gradeSystem")}
                  </Label>
                </div>
                <Select
                  value={learningPrefs.grade_system}
                  onValueChange={(v) => {
                    const next = v as GradeSystem;
                    const max = next === "suisse" ? 11 : 12;
                    onLearningPrefsChange({
                      grade_system: next,
                      age_group: next === "suisse" ? "" : learningPrefs.age_group,
                      grade_level:
                        learningPrefs.grade_level && parseInt(learningPrefs.grade_level, 10) > max
                          ? ""
                          : learningPrefs.grade_level,
                    });
                  }}
                  disabled={isUpdatingProfile}
                >
                  <SelectTrigger
                    id="grade_system"
                    className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {GRADE_SYSTEMS.map((sys) => (
                      <SelectItem key={sys} value={sys}>
                        {tOnboarding(`gradeSystems.${sys}`)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Niveau */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <Label htmlFor="grade_level" className="text-sm font-medium text-foreground">
                    {tLearning("gradeLevel")}
                  </Label>
                </div>
                <Select
                  value={learningPrefs.grade_level}
                  onValueChange={(value) => onLearningPrefsChange({ grade_level: value })}
                  disabled={isUpdatingProfile}
                >
                  <SelectTrigger
                    id="grade_level"
                    aria-label={tLearning("gradeLevel")}
                    className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                  >
                    <SelectValue placeholder={tLearning("gradeLevelPlaceholder")} />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.from(
                      { length: learningPrefs.grade_system === "suisse" ? 11 : 12 },
                      (_, i) => i + 1
                    ).map((level) => (
                      <SelectItem key={level} value={level.toString()}>
                        {learningPrefs.grade_system === "suisse" ? `${level}H` : level}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Tranche d'âge (unifié seulement) */}
              {learningPrefs.grade_system === "unifie" && (
                <div className="flex flex-col sm:flex-row sm:items-start justify-between py-4 border-b border-border/50 last:border-0 gap-2">
                  <div className="flex flex-col gap-1 pr-4">
                    <Label htmlFor="age_group_band" className="text-sm font-medium text-foreground">
                      {tLearning("ageGroupBand")}
                    </Label>
                    <p className="text-xs text-muted-foreground max-w-md">
                      {tLearning("ageGroupBandHint")}
                    </p>
                  </div>
                  <Select
                    value={learningPrefs.age_group || "none"}
                    onValueChange={(value) =>
                      onLearningPrefsChange({ age_group: value === "none" ? "" : value })
                    }
                    disabled={isUpdatingProfile}
                  >
                    <SelectTrigger
                      id="age_group_band"
                      aria-label={tLearning("ageGroupBand")}
                      className="w-full sm:w-[250px] mt-1 sm:mt-0 shrink-0"
                    >
                      <SelectValue placeholder={tLearning("ageGroupBandPlaceholder")} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">{tLearning("ageGroupBandPlaceholder")}</SelectItem>
                      {USER_PROFILE_AGE_GROUPS.map((band) => (
                        <SelectItem key={band} value={band}>
                          {tLearning(`ageGroupBands.${band}`)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* Style d'apprentissage */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <Label htmlFor="learning_style" className="text-sm font-medium text-foreground">
                    {tLearning("learningStyle")}
                  </Label>
                </div>
                <Select
                  value={learningPrefs.learning_style}
                  onValueChange={(value) => onLearningPrefsChange({ learning_style: value })}
                  disabled={isUpdatingProfile}
                >
                  <SelectTrigger
                    id="learning_style"
                    aria-label={tLearning("learningStyle")}
                    className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                  >
                    <SelectValue placeholder={tLearning("learningStylePlaceholder")} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="visuel">{t("learningStyles.visuel")}</SelectItem>
                    <SelectItem value="auditif">{t("learningStyles.auditif")}</SelectItem>
                    <SelectItem value="kinesthésique">
                      {t("learningStyles.kinesthésique")}
                    </SelectItem>
                    <SelectItem value="lecture">{t("learningStyles.lecture")} </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Difficulté préférée */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <Label
                    htmlFor="preferred_difficulty"
                    className="text-sm font-medium text-foreground"
                  >
                    {tLearning("preferredAgeGroup")}
                  </Label>
                </div>
                <Select
                  value={learningPrefs.preferred_difficulty}
                  onValueChange={(value) => onLearningPrefsChange({ preferred_difficulty: value })}
                  disabled={isUpdatingProfile}
                >
                  <SelectTrigger
                    id="preferred_difficulty"
                    aria-label={tLearning("preferredAgeGroup")}
                    className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                  >
                    <SelectValue placeholder={tLearning("preferredAgeGroupPlaceholder")} />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.values(AGE_GROUPS).map((group) => (
                      <SelectItem key={group} value={group}>
                        {getAgeDisplay(group)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Objectif */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <Label htmlFor="learning_goal" className="text-sm font-medium text-foreground">
                    {tOnboarding("learningGoal")}
                  </Label>
                </div>
                <Select
                  value={learningPrefs.learning_goal || "none"}
                  onValueChange={(v) =>
                    onLearningPrefsChange({ learning_goal: v === "none" ? "" : v })
                  }
                  disabled={isUpdatingProfile}
                >
                  <SelectTrigger
                    id="learning_goal"
                    className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                  >
                    <SelectValue placeholder={tOnboarding("learningGoalPlaceholder")} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">—</SelectItem>
                    {LEARNING_GOALS.map((g) => (
                      <SelectItem key={g} value={g}>
                        {tOnboarding(`goals.${g}`)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Rythme */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <Label htmlFor="practice_rhythm" className="text-sm font-medium text-foreground">
                    {tOnboarding("practiceRhythm")}
                  </Label>
                </div>
                <Select
                  value={learningPrefs.practice_rhythm || "none"}
                  onValueChange={(v) =>
                    onLearningPrefsChange({ practice_rhythm: v === "none" ? "" : v })
                  }
                  disabled={isUpdatingProfile}
                >
                  <SelectTrigger
                    id="practice_rhythm"
                    className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                  >
                    <SelectValue placeholder={tOnboarding("practiceRhythmPlaceholder")} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">—</SelectItem>
                    {PRACTICE_RHYTHMS.map((r) => (
                      <SelectItem key={r} value={r}>
                        {tOnboarding(`rhythms.${r}`)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Actions */}
              <div className="flex gap-2 justify-end pt-6">
                <Button
                  variant="outline"
                  onClick={onCancel}
                  disabled={isUpdatingProfile}
                  aria-label={tActions("cancel")}
                >
                  <X className="mr-2 h-4 w-4" />
                  {tActions("cancel")}
                </Button>
                <Button
                  onClick={onSave}
                  disabled={isUpdatingProfile}
                  aria-label={tActions("save")}
                  aria-busy={isUpdatingProfile}
                >
                  {isUpdatingProfile ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {tActions("saving")}
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      {tActions("save")}
                    </>
                  )}
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col">
              {user.grade_system && (
                <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                  <div className="flex flex-col gap-1 pr-4">
                    <p className="text-sm font-medium text-foreground">
                      {tOnboarding("gradeSystem")}
                    </p>
                  </div>
                  <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                    {tOnboarding(`gradeSystems.${user.grade_system}`)}
                  </p>
                </div>
              )}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <p className="text-sm font-medium text-foreground">{tLearning("gradeLevel")}</p>
                </div>
                <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                  {user.grade_level
                    ? user.grade_system === "suisse"
                      ? `${user.grade_level}H`
                      : user.grade_level
                    : "-"}
                </p>
              </div>
              {user.grade_system === "unifie" && (
                <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                  <div className="flex flex-col gap-1 pr-4">
                    <p className="text-sm font-medium text-foreground">
                      {tLearning("ageGroupBand")}
                    </p>
                  </div>
                  <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                    {user.age_group &&
                    USER_PROFILE_AGE_GROUPS.includes(user.age_group as UserProfileAgeGroup)
                      ? tLearning(`ageGroupBands.${user.age_group}`)
                      : "—"}
                  </p>
                </div>
              )}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <p className="text-sm font-medium text-foreground">
                    {tLearning("learningStyle")}
                  </p>
                </div>
                <p className="text-base font-medium text-foreground sm:text-right capitalize mt-3 sm:mt-0 shrink-0">
                  {user.learning_style || "-"}
                </p>
              </div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <p className="text-sm font-medium text-foreground">
                    {tLearning("preferredAgeGroup")}
                  </p>
                </div>
                <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                  {user.preferred_difficulty
                    ? Object.values(AGE_GROUPS).includes(user.preferred_difficulty as AgeGroup)
                      ? getAgeDisplay(user.preferred_difficulty)
                      : user.preferred_difficulty
                    : "-"}
                </p>
              </div>
              {user.learning_goal && (
                <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                  <div className="flex flex-col gap-1 pr-4">
                    <p className="text-sm font-medium text-foreground">
                      {tOnboarding("learningGoal")}
                    </p>
                  </div>
                  <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                    {LEARNING_GOALS.includes(user.learning_goal as (typeof LEARNING_GOALS)[number])
                      ? tOnboarding(`goals.${user.learning_goal}`)
                      : user.learning_goal}
                  </p>
                </div>
              )}
              {user.practice_rhythm && (
                <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                  <div className="flex flex-col gap-1 pr-4">
                    <p className="text-sm font-medium text-foreground">
                      {tOnboarding("practiceRhythm")}
                    </p>
                  </div>
                  <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                    {PRACTICE_RHYTHMS.includes(
                      user.practice_rhythm as (typeof PRACTICE_RHYTHMS)[number]
                    )
                      ? tOnboarding(`rhythms.${user.practice_rhythm}`)
                      : user.practice_rhythm}
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
