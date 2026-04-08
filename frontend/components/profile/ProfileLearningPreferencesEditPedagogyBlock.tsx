"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AGE_GROUPS } from "@/lib/constants/exercises";
import type { LearningPrefsState } from "@/hooks/useProfilePageController";

interface ProfileLearningPreferencesEditPedagogyBlockProps {
  learningPrefs: LearningPrefsState;
  isUpdatingProfile: boolean;
  onLearningPrefsChange: (update: Partial<LearningPrefsState>) => void;
  tProfile: (key: string) => string;
  tLearning: (key: string) => string;
  getAgeDisplay: (group: string) => string;
}

export function ProfileLearningPreferencesEditPedagogyBlock({
  learningPrefs,
  isUpdatingProfile,
  onLearningPrefsChange,
  tProfile,
  tLearning,
  getAgeDisplay,
}: ProfileLearningPreferencesEditPedagogyBlockProps) {
  return (
    <>
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
            <SelectItem value="visuel">{tProfile("learningStyles.visuel")}</SelectItem>
            <SelectItem value="auditif">{tProfile("learningStyles.auditif")}</SelectItem>
            <SelectItem value="kinesthésique">
              {tProfile("learningStyles.kinesthésique")}
            </SelectItem>
            <SelectItem value="lecture">{tProfile("learningStyles.lecture")} </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
        <div className="flex flex-col gap-1 pr-4">
          <Label htmlFor="preferred_difficulty" className="text-sm font-medium text-foreground">
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
    </>
  );
}
