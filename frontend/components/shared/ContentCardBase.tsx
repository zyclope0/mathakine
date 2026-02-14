"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
interface ContentCardBaseProps {
  completed: boolean;
  titleId: string;
  descriptionId: string;
  completedLabel: string;
  completedAriaLabel?: string;
  children: React.ReactNode;
}

/**
 * Base partagée pour ExerciseCard et ChallengeCard (DRY).
 * Gère : motion wrapper, Card shell, badge "Résolu".
 */
export function ContentCardBase({
  completed,
  titleId,
  descriptionId,
  completedLabel,
  completedAriaLabel,
  children,
}: ContentCardBaseProps) {
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  const variants = createVariants({
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
  });

  const transition = createTransition({ duration: 0.2 });

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={transition}
      whileHover={!shouldReduceMotion ? { y: -4 } : {}}
    >
      <Card
        className="card-spatial-depth relative"
        role="article"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
      >
        {completed && (
          <Badge
            variant="default"
            className="absolute top-2 right-2 z-10 bg-green-500/90 text-white border-green-600 shadow-lg"
            aria-label={completedAriaLabel ?? completedLabel}
          >
            <CheckCircle2 className="h-3 w-3 mr-1" aria-hidden="true" />
            {completedLabel}
          </Badge>
        )}
        {children}
      </Card>
    </motion.div>
  );
}
