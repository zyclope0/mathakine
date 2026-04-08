"use client";

import { formatDistanceToNow } from "date-fns";
import { enUS, fr } from "date-fns/locale";
import { useTranslations } from "next-intl";

interface DashboardLastUpdateProps {
  time: string;
  locale?: string;
}

export function DashboardLastUpdate({ time, locale }: DashboardLastUpdateProps) {
  const t = useTranslations("dashboard");

  let displayTime: string;
  try {
    const date = new Date(time);
    const dateLocale = locale === "en" ? enUS : fr;
    displayTime = formatDistanceToNow(date, { addSuffix: true, locale: dateLocale });
  } catch {
    displayTime = time;
  }

  return <p className="text-sm text-muted-foreground">{t("lastUpdate", { time: displayTime })}</p>;
}
