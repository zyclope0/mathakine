"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CalendarDays } from "lucide-react";
import { useTranslations } from "next-intl";
import { type TimeRange } from "@/hooks/useUserStats";
import { cn } from "@/lib/utils";

interface TimeRangeSelectorProps {
  value: TimeRange;
  onValueChange: (value: TimeRange) => void;
  className?: string;
  triggerClassName?: string;
}

export function TimeRangeSelector({
  value,
  onValueChange,
  className,
  triggerClassName,
}: TimeRangeSelectorProps) {
  const t = useTranslations("dashboard.timeRange");

  return (
    <div className={className}>
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger
          className={cn("flex min-h-11 w-[180px] items-center gap-2 sm:min-h-9", triggerClassName)}
        >
          <CalendarDays className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <SelectValue placeholder={t("30days")} />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="7">{t("7days", { default: "7 derniers jours" })}</SelectItem>
          <SelectItem value="30">{t("30days", { default: "30 derniers jours" })}</SelectItem>
          <SelectItem value="90">{t("90days", { default: "3 derniers mois" })}</SelectItem>
          <SelectItem value="all">{t("all", { default: "Tout" })}</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
