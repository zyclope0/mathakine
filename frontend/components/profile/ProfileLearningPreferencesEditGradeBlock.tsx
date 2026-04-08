"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { USER_PROFILE_AGE_GROUPS } from "@/lib/constants/userProfileAgeGroup";
import {
  buildPatchWhenGradeSystemChanges,
  gradeLevelSelectOptionCount,
} from "@/lib/profile/profileLearningPreferences";
import { GRADE_SYSTEMS, type GradeSystem } from "@/lib/profile/profilePage";
import type { LearningPrefsState } from "@/hooks/useProfilePageController";

interface ProfileLearningPreferencesEditGradeBlockProps {
  learningPrefs: LearningPrefsState;
  isUpdatingProfile: boolean;
  onLearningPrefsChange: (update: Partial<LearningPrefsState>) => void;
  tOnboarding: (key: string) => string;
  tLearning: (key: string) => string;
}

export function ProfileLearningPreferencesEditGradeBlock({
  learningPrefs,
  isUpdatingProfile,
  onLearningPrefsChange,
  tOnboarding,
  tLearning,
}: ProfileLearningPreferencesEditGradeBlockProps) {
  const optionCount = gradeLevelSelectOptionCount(learningPrefs.grade_system);

  return (
    <>
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
            onLearningPrefsChange(buildPatchWhenGradeSystemChanges(learningPrefs, next));
          }}
          disabled={isUpdatingProfile}
        >
          <SelectTrigger id="grade_system" className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
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
            {Array.from({ length: optionCount }, (_, i) => i + 1).map((level) => (
              <SelectItem key={level} value={level.toString()}>
                {learningPrefs.grade_system === "suisse" ? `${level}H` : level}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

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
    </>
  );
}
