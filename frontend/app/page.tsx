"use client";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { PageLayout } from "@/components/layout";
import { LogoBadge } from "@/components/LogoBadge";
import { useTranslations } from "next-intl";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { cn } from "@/lib/utils";
import dynamic from "next/dynamic";

// AcademyStatsWidget — chargé uniquement pour les visiteurs non-connectés (NI-6)
const AcademyStatsWidgetLazy = dynamic(
  () =>
    import("@/components/home/AcademyStatsWidget").then((mod) => ({
      default: mod.AcademyStatsWidget,
    })),
  {
    ssr: false,
    loading: () => (
      <div className="border border-border/40 rounded-xl bg-card/40">
        <div className="py-6 px-4">
          <div className="flex flex-wrap gap-8 justify-center">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="text-center space-y-2">
                <Skeleton className="h-6 w-12 mx-auto" />
                <Skeleton className="h-4 w-20 mx-auto" />
              </div>
            ))}
          </div>
        </div>
      </div>
    ),
  }
);

/**
 * Page d'accueil Mathakine
 */
export default function HomePage() {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const t = useTranslations("home");
  const { shouldReduceMotion } = useAccessibleAnimation();

  return (
    <PageLayout>
      {/* Hero Section */}
      <section className="text-center py-6 md:py-12 space-y-4" aria-labelledby="hero-title">
        <div
          className={cn(
            "flex flex-col items-center",
            !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4"
          )}
        >
          <LogoBadge alt={t("hero.title")} className="mb-6" />
          <h1
            id="hero-title"
            className={cn(
              "text-4xl md:text-5xl lg:text-6xl font-extrabold text-foreground mb-4 tracking-tight",
              !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4 animation-delay-100"
            )}
          >
            {t("hero.titleTagline1")}
            <br />
            {t("hero.titleTagline2")}
          </h1>
        </div>
        <p
          className={cn(
            "text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto",
            !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4 animation-delay-200"
          )}
        >
          {t("hero.subtitle")}
        </p>

        {/* CTAs */}
        <div
          className={cn(
            "flex flex-wrap gap-4 justify-center",
            !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4 animation-delay-400"
          )}
        >
          {isAuthenticated ? (
            <Button asChild size="lg" className="w-full sm:w-auto">
              <Link href="/dashboard">
                {t("hero.ctaDashboard")}
                <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
              </Link>
            </Button>
          ) : (
            <Button asChild size="lg" className="w-full sm:w-auto">
              <Link href="/register">
                {t("hero.ctaStart")}
                <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
              </Link>
            </Button>
          )}
          <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
            <Link href="/exercises">{t("hero.ctaDiscoverExercises")}</Link>
          </Button>
        </div>
      </section>

      {/* Stats de l'Académie — visiteurs non-connectés uniquement (NI-6)
          Guard !isAuthLoading : évite le flash du widget pendant la résolution de la query auth */}
      {!isAuthLoading && !isAuthenticated && (
        <section className="py-2" aria-label="Statistiques de l'Académie">
          <AcademyStatsWidgetLazy />
        </section>
      )}

      {/* Fonctionnalités — layout asymétrique (NI-6) */}
      <section
        className="pt-4 pb-8 md:pt-6 md:pb-16 space-y-6 md:space-y-12"
        aria-labelledby="features-title"
      >
        <div className="space-y-2">
          <h2 id="features-title" className="text-2xl md:text-3xl font-bold">
            {t("features.title")}
          </h2>
          <p className="text-muted-foreground text-sm md:text-base max-w-lg">
            {t("features.description")}
          </p>
        </div>

        {/* Feature principale — large */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          <div className="md:col-span-2 border border-border/40 rounded-2xl p-8 md:p-10 bg-card/60 min-h-40 md:min-h-56 flex flex-col justify-center">
            <p className="section-eyebrow-accent mb-3">{t("features.feature1.label")}</p>
            <h3 className="text-xl md:text-2xl font-bold text-foreground tracking-tight mb-3">
              {t("features.feature1.title")}
            </h3>
            <p className="text-muted-foreground text-sm md:text-base max-w-prose">
              {t("features.feature1.description")}
            </p>
          </div>

          {/* Feature secondaire — Défis */}
          <div className="border border-border/40 rounded-2xl p-6 md:p-8">
            <h3 className="section-title-sm md:text-lg mb-2">{t("features.feature2.title")}</h3>
            <p className="text-muted-foreground text-sm">{t("features.feature2.description")}</p>
          </div>

          {/* Feature secondaire — Gamification */}
          <div className="border border-border/40 rounded-2xl p-6 md:p-8">
            <h3 className="section-title-sm md:text-lg mb-2">{t("features.feature3.title")}</h3>
            <p className="text-muted-foreground text-sm">{t("features.feature3.description")}</p>
          </div>
        </div>

        {/* Feature tertiaire — Accessibilité — bande texte */}
        <div className="border-t border-border/30 pt-6 flex flex-col sm:flex-row sm:items-center gap-3">
          <p className="text-sm font-medium text-foreground">{t("features.feature4.title")}</p>
          <span className="hidden sm:block text-border/60" aria-hidden="true">
            —
          </span>
          <p className="text-sm text-muted-foreground">{t("features.feature4.description")}</p>
        </div>
      </section>
    </PageLayout>
  );
}
