"use client";

import {
  USER_PROFILE_AGE_GROUPS,
  type UserProfileAgeGroup,
} from "@/lib/constants/userProfileAgeGroup";
import {
  formatGradeLevelReadValue,
  isKnownLearningGoal,
  isKnownPracticeRhythm,
  resolvePreferredDifficultyReadLabel,
} from "@/lib/profile/profileLearningPreferences";
interface ProfileLearningPreferencesReadSummaryUser {
  grade_system?: string | null;
  grade_level?: number | null;
  age_group?: string | null;
  learning_style?: string | null;
  preferred_difficulty?: string | null;
  learning_goal?: string | null;
  practice_rhythm?: string | null;
}

interface ProfileLearningPreferencesReadSummaryProps {
  user: ProfileLearningPreferencesReadSummaryUser;
  getAgeDisplay: (group: string) => string;
  tOnboarding: (key: string) => string;
  tLearning: (key: string) => string;
}

export function ProfileLearningPreferencesReadSummary({
  user,
  getAgeDisplay,
  tOnboarding,
  tLearning,
}: ProfileLearningPreferencesReadSummaryProps) {
  return (
    <div className="flex flex-col">
      {user.grade_system && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
          <div className="flex flex-col gap-1 pr-4">
            <p className="text-sm font-medium text-foreground">{tOnboarding("gradeSystem")}</p>
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
          {formatGradeLevelReadValue(user.grade_system, user.grade_level ?? undefined)}
        </p>
      </div>
      {user.grade_system === "unifie" && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
          <div className="flex flex-col gap-1 pr-4">
            <p className="text-sm font-medium text-foreground">{tLearning("ageGroupBand")}</p>
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
          <p className="text-sm font-medium text-foreground">{tLearning("learningStyle")}</p>
        </div>
        <p className="text-base font-medium text-foreground sm:text-right capitalize mt-3 sm:mt-0 shrink-0">
          {user.learning_style || "-"}
        </p>
      </div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
        <div className="flex flex-col gap-1 pr-4">
          <p className="text-sm font-medium text-foreground">{tLearning("preferredAgeGroup")}</p>
        </div>
        <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
          {resolvePreferredDifficultyReadLabel(user.preferred_difficulty, getAgeDisplay)}
        </p>
      </div>
      {user.learning_goal && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
          <div className="flex flex-col gap-1 pr-4">
            <p className="text-sm font-medium text-foreground">{tOnboarding("learningGoal")}</p>
          </div>
          <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
            {isKnownLearningGoal(user.learning_goal)
              ? tOnboarding(`goals.${user.learning_goal}`)
              : user.learning_goal}
          </p>
        </div>
      )}
      {user.practice_rhythm && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
          <div className="flex flex-col gap-1 pr-4">
            <p className="text-sm font-medium text-foreground">{tOnboarding("practiceRhythm")}</p>
          </div>
          <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
            {isKnownPracticeRhythm(user.practice_rhythm)
              ? tOnboarding(`rhythms.${user.practice_rhythm}`)
              : user.practice_rhythm}
          </p>
        </div>
      )}
    </div>
  );
}
