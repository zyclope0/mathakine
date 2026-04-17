import { AlertTriangle, Bug, FileQuestion, MessageCircle } from "lucide-react";

/**
 * Single source of truth for in-app feedback categories (FAB + contextual triggers).
 * Subject lines for mailto fallback are resolved via next-intl keys: exerciseSubject, etc.
 */
export const FEEDBACK_TYPES = [
  { id: "exercise" as const, icon: FileQuestion, subjectKey: "exerciseSubject" },
  { id: "challenge" as const, icon: AlertTriangle, subjectKey: "challengeSubject" },
  { id: "ui" as const, icon: Bug, subjectKey: "uiSubject" },
  { id: "other" as const, icon: MessageCircle, subjectKey: "otherSubject" },
] as const;

export type FeedbackTypeId = (typeof FEEDBACK_TYPES)[number]["id"];

export type FeedbackContext = {
  exerciseId?: number;
  challengeId?: number;
};
