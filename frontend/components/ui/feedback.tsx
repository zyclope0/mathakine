"use client";

import { cn } from "@/lib/utils/cn";
import { CheckCircle2, XCircle, AlertCircle, Info } from "lucide-react";
import { useEffect, useState } from "react";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";

export type FeedbackType = "success" | "error" | "warning" | "info";

interface FeedbackProps {
  type: FeedbackType;
  message: string;
  className?: string;
  autoHide?: boolean;
  duration?: number;
  onClose?: () => void;
}

const icons = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertCircle,
  info: Info,
};

const styles = {
  success:
    "bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200",
  error:
    "bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200",
  warning:
    "bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200",
  info: "bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200",
};

/**
 * Feedback - Composant pour afficher des messages de feedback visuel
 *
 * Types : success, error, warning, info
 * Supporte auto-hide et animations accessibles
 */
export function Feedback({
  type,
  message,
  className,
  autoHide = false,
  duration = 3000,
  onClose,
}: FeedbackProps) {
  const [isVisible, setIsVisible] = useState(true);
  const { shouldReduceMotion } = useAccessibleAnimation();
  const Icon = icons[type];

  useEffect(() => {
    if (autoHide) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [autoHide, duration, onClose]);

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-lg border p-4",
        styles[type],
        shouldReduceMotion ? "" : "animate-in slide-in-from-top-2",
        className
      )}
      role="alert"
      aria-live="polite"
    >
      <Icon
        className={cn("h-5 w-5 shrink-0 mt-0.5", shouldReduceMotion ? "" : "animate-in zoom-in-50")}
        aria-hidden="true"
      />
      <p className="flex-1 text-sm font-medium">{message}</p>
      {onClose && (
        <button
          onClick={() => {
            setIsVisible(false);
            onClose();
          }}
          className="ml-auto shrink-0 rounded-md p-1 hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
          aria-label="Fermer"
        >
          <XCircle className="h-4 w-4" aria-hidden="true" />
        </button>
      )}
    </div>
  );
}

/**
 * SuccessFeedback - Raccourci pour feedback de succès
 */
export function SuccessFeedback({ message, ...props }: Omit<FeedbackProps, "type">) {
  return <Feedback type="success" message={message} {...props} />;
}

/**
 * ErrorFeedback - Raccourci pour feedback d'erreur
 */
export function ErrorFeedback({ message, ...props }: Omit<FeedbackProps, "type">) {
  return <Feedback type="error" message={message} {...props} />;
}

/**
 * WarningFeedback - Raccourci pour feedback d'avertissement
 */
export function WarningFeedback({ message, ...props }: Omit<FeedbackProps, "type">) {
  return <Feedback type="warning" message={message} {...props} />;
}

/**
 * InfoFeedback - Raccourci pour feedback d'information
 */
export function InfoFeedback({ message, ...props }: Omit<FeedbackProps, "type">) {
  return <Feedback type="info" message={message} {...props} />;
}
