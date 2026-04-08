"use client";

import { Button } from "@/components/ui/button";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { Settings, Pencil } from "lucide-react";

interface ProfileLearningPreferencesHeaderProps {
  isEditing: boolean;
  title: string;
  editLabel: string;
  onStartEditing: () => void;
}

export function ProfileLearningPreferencesHeader({
  isEditing,
  title,
  editLabel,
  onStartEditing,
}: ProfileLearningPreferencesHeaderProps) {
  return (
    <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
      <div className="flex items-center justify-between">
        <CardTitle className="flex items-center gap-2 text-xl">
          <Settings className="h-5 w-5 text-primary" />
          {title}
        </CardTitle>
        {!isEditing && (
          <Button
            variant="outline"
            size="sm"
            onClick={onStartEditing}
            aria-label={editLabel}
            className="inline-flex items-center gap-2 border-border hover:bg-accent hover:text-accent-foreground rounded-lg h-9 px-3"
          >
            <Pencil className="h-3.5 w-3.5" />
            {editLabel}
          </Button>
        )}
      </div>
    </CardHeader>
  );
}
