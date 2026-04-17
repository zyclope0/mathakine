"use client";

import { useState, useRef, useEffect } from "react";
import { Flag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import { FeedbackComposer } from "@/components/feedback/FeedbackComposer";
import { useFeedbackFlow } from "@/components/feedback/useFeedbackFlow";
import { FEEDBACK_TYPES, type FeedbackContext } from "@/components/feedback/feedbackConfig";

export type { FeedbackContext };

interface FeedbackFabProps {
  context?: FeedbackContext;
  className?: string;
  componentId?: string;
}

export function FeedbackFab({ context: contextProp, className, componentId }: FeedbackFabProps) {
  const t = useTranslations("feedback.fab");
  const flow = useFeedbackFlow({
    ...(contextProp !== undefined ? { context: contextProp } : {}),
    ...(componentId !== undefined ? { componentId } : {}),
  });
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (type: (typeof FEEDBACK_TYPES)[number]["id"]) => {
    flow.openModalForType(type);
    setIsOpen(false);
  };

  return (
    <>
      <div
        ref={dropdownRef}
        className={cn("fixed bottom-6 right-6 z-[9985] feedback-fab", className)}
      >
        <div
          className={cn(
            "absolute bottom-14 right-0 mb-2 flex flex-col gap-1 rounded-lg border bg-card p-1 shadow-lg transition-opacity",
            isOpen ? "opacity-100" : "pointer-events-none opacity-0"
          )}
        >
          {FEEDBACK_TYPES.map(({ id, icon: Icon }) => (
            <Button
              key={id}
              variant="ghost"
              size="sm"
              className="justify-start gap-2"
              onClick={() => handleSelect(id)}
            >
              <Icon className="h-4 w-4" />
              {flow.getTypeLabel(id)}
            </Button>
          ))}
        </div>
        <Button
          variant="default"
          size="icon"
          className="h-12 w-12 rounded-full shadow-lg bg-[#FFCCCC] hover:bg-[#FFB3B3] text-[#C00030]"
          onClick={() => setIsOpen(!isOpen)}
          aria-label={t("buttonLabel", { default: "Signaler un problème" })}
          aria-expanded={isOpen}
        >
          <Flag className="h-5 w-5" />
        </Button>
      </div>

      <FeedbackComposer
        open={flow.modalOpen}
        onOpenChange={flow.setModalOpen}
        selectedType={flow.selectedType}
        description={flow.description}
        onDescriptionChange={flow.setDescription}
        isSubmitting={flow.isSubmitting}
        onSubmit={flow.handleSubmit}
        getTypeLabel={flow.getTypeLabel}
      />
    </>
  );
}
