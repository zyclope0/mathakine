"use client";

import { BarChart3, LayoutDashboard, TrendingUp, Zap } from "lucide-react";
import { useTranslations } from "next-intl";
import { TabsList, TabsTrigger } from "@/components/ui/tabs";

export function DashboardTabsNav() {
  const t = useTranslations("dashboard");

  return (
    <div className="w-full overflow-x-auto pb-1 -mb-1 no-scrollbar">
      <TabsList
        className="inline-flex h-11 w-max min-w-full sm:w-full sm:max-w-3xl"
        aria-label={t("tabs.tabsLabel", { default: "Sections du tableau de bord" })}
      >
        <TabsTrigger value="overview" className="flex flex-1 items-center gap-1.5 px-3 text-sm">
          <LayoutDashboard className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span className="hidden sm:inline">
            {t("tabs.overview", { default: "Vue d'ensemble" })}
          </span>
          <span className="sm:hidden">{t("tabs.overviewShort", { default: "Vue" })}</span>
        </TabsTrigger>
        <TabsTrigger
          value="recommendations"
          className="flex flex-1 items-center gap-1.5 px-3 text-sm"
        >
          <Zap className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span className="hidden sm:inline">
            {t("tabs.recommendations", { default: "Recommandations" })}
          </span>
          <span className="sm:hidden">{t("tabs.recommendationsShort", { default: "Recos" })}</span>
        </TabsTrigger>
        <TabsTrigger value="progress" className="flex flex-1 items-center gap-1.5 px-3 text-sm">
          <TrendingUp className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span className="hidden sm:inline">{t("tabs.progress", { default: "Progression" })}</span>
          <span className="sm:hidden">{t("tabs.progressShort")}</span>
        </TabsTrigger>
        <TabsTrigger value="profile" className="flex flex-1 items-center gap-1.5 px-3 text-sm">
          <BarChart3 className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span className="hidden sm:inline">{t("tabs.profile", { default: "Mon Profil" })}</span>
          <span className="sm:hidden">{t("tabs.profileShort", { default: "Profil" })}</span>
        </TabsTrigger>
      </TabsList>
    </div>
  );
}
