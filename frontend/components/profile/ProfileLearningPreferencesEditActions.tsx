"use client";

import { Button } from "@/components/ui/button";
import { Save, X, Loader2 } from "lucide-react";

interface ProfileLearningPreferencesEditActionsProps {
  isUpdatingProfile: boolean;
  cancelLabel: string;
  saveLabel: string;
  savingLabel: string;
  onCancel: () => void;
  onSave: () => void;
}

export function ProfileLearningPreferencesEditActions({
  isUpdatingProfile,
  cancelLabel,
  saveLabel,
  savingLabel,
  onCancel,
  onSave,
}: ProfileLearningPreferencesEditActionsProps) {
  return (
    <div className="flex gap-2 justify-end pt-6">
      <Button
        variant="outline"
        onClick={onCancel}
        disabled={isUpdatingProfile}
        aria-label={cancelLabel}
      >
        <X className="mr-2 h-4 w-4" />
        {cancelLabel}
      </Button>
      <Button
        onClick={onSave}
        disabled={isUpdatingProfile}
        aria-label={saveLabel}
        aria-busy={isUpdatingProfile}
      >
        {isUpdatingProfile ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            {savingLabel}
          </>
        ) : (
          <>
            <Save className="mr-2 h-4 w-4" />
            {saveLabel}
          </>
        )}
      </Button>
    </div>
  );
}
