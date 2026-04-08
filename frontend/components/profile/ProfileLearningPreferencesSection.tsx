"use client";

import { Card, CardContent } from "@/components/ui/card";
import { useTranslations } from "next-intl";
import type { LearningPrefsState } from "@/hooks/useProfilePageController";
import { ProfileLearningPreferencesEditActions } from "@/components/profile/ProfileLearningPreferencesEditActions";
import { ProfileLearningPreferencesEditGoalsBlock } from "@/components/profile/ProfileLearningPreferencesEditGoalsBlock";
import { ProfileLearningPreferencesEditGradeBlock } from "@/components/profile/ProfileLearningPreferencesEditGradeBlock";
import { ProfileLearningPreferencesEditPedagogyBlock } from "@/components/profile/ProfileLearningPreferencesEditPedagogyBlock";
import { ProfileLearningPreferencesHeader } from "@/components/profile/ProfileLearningPreferencesHeader";
import { ProfileLearningPreferencesReadSummary } from "@/components/profile/ProfileLearningPreferencesReadSummary";

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
 * Façade FFI-L11 + FFI-L18A — sous-blocs dans le même dossier.
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
        <ProfileLearningPreferencesHeader
          isEditing={isEditing}
          title={tLearning("title")}
          editLabel={tActions("edit")}
          onStartEditing={onStartEditing}
        />
        <CardContent className="p-0">
          {isEditing ? (
            <div className="flex flex-col">
              <ProfileLearningPreferencesEditGradeBlock
                learningPrefs={learningPrefs}
                isUpdatingProfile={isUpdatingProfile}
                onLearningPrefsChange={onLearningPrefsChange}
                tOnboarding={tOnboarding}
                tLearning={tLearning}
              />
              <ProfileLearningPreferencesEditPedagogyBlock
                learningPrefs={learningPrefs}
                isUpdatingProfile={isUpdatingProfile}
                onLearningPrefsChange={onLearningPrefsChange}
                tProfile={t}
                tLearning={tLearning}
                getAgeDisplay={getAgeDisplay}
              />
              <ProfileLearningPreferencesEditGoalsBlock
                learningPrefs={learningPrefs}
                isUpdatingProfile={isUpdatingProfile}
                onLearningPrefsChange={onLearningPrefsChange}
                tOnboarding={tOnboarding}
              />
              <ProfileLearningPreferencesEditActions
                isUpdatingProfile={isUpdatingProfile}
                cancelLabel={tActions("cancel")}
                saveLabel={tActions("save")}
                savingLabel={tActions("saving")}
                onCancel={onCancel}
                onSave={onSave}
              />
            </div>
          ) : (
            <ProfileLearningPreferencesReadSummary
              user={user}
              getAgeDisplay={getAgeDisplay}
              tOnboarding={tOnboarding}
              tLearning={tLearning}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
