"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { LEARNING_GOALS, PRACTICE_RHYTHMS } from "@/lib/profile/profilePage";
import type { LearningPrefsState } from "@/hooks/useProfilePageController";

interface ProfileLearningPreferencesEditGoalsBlockProps {
  learningPrefs: LearningPrefsState;
  isUpdatingProfile: boolean;
  onLearningPrefsChange: (update: Partial<LearningPrefsState>) => void;
  tOnboarding: (key: string) => string;
}

export function ProfileLearningPreferencesEditGoalsBlock({
  learningPrefs,
  isUpdatingProfile,
  onLearningPrefsChange,
  tOnboarding,
}: ProfileLearningPreferencesEditGoalsBlockProps) {
  return (
    <>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
        <div className="flex flex-col gap-1 pr-4">
          <Label htmlFor="learning_goal" className="text-sm font-medium text-foreground">
            {tOnboarding("learningGoal")}
          </Label>
        </div>
        <Select
          value={learningPrefs.learning_goal || "none"}
          onValueChange={(v) => onLearningPrefsChange({ learning_goal: v === "none" ? "" : v })}
          disabled={isUpdatingProfile}
        >
          <SelectTrigger id="learning_goal" className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
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

      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
        <div className="flex flex-col gap-1 pr-4">
          <Label htmlFor="practice_rhythm" className="text-sm font-medium text-foreground">
            {tOnboarding("practiceRhythm")}
          </Label>
        </div>
        <Select
          value={learningPrefs.practice_rhythm || "none"}
          onValueChange={(v) => onLearningPrefsChange({ practice_rhythm: v === "none" ? "" : v })}
          disabled={isUpdatingProfile}
        >
          <SelectTrigger id="practice_rhythm" className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
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
    </>
  );
}
