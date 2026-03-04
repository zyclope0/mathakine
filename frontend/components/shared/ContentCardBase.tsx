"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { cn } from "@/lib/utils";

interface ContentCardBaseProps {
  completed: boolean;
  titleId: string;
  descriptionId: string;
  completedLabel: string;
  completedAriaLabel?: string;
  /** Rend la carte entière cliquable (ex: ouvrir une modal). */
  onClick?: () => void;
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
  onClick,
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
      onClick={onClick}
      className={cn("h-full", onClick && "cursor-pointer")}
    >
      <Card
        className={cn(
          "card-spatial-depth relative group h-full flex flex-col",
          "transition-all duration-300",
          onClick && "hover:border-primary/50 hover:shadow-[0_0_15px_hsl(var(--primary)/0.15)]"
        )}
        role="article"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
      >
        {/* Badge "Résolu" — fond teinté discret */}
        {completed && (
          <Badge
            variant="outline"
            className="absolute top-2 right-2 z-10 bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
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
