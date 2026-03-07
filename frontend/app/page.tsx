"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";
import Link from "next/link";
import { BookOpen, Zap, Trophy, Users, ArrowRight } from "lucide-react";
import { PageLayout } from "@/components/layout";
import { LogoBadge } from "@/components/LogoBadge";
import { useTranslations } from "next-intl";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { cn } from "@/lib/utils";
import dynamic from "next/dynamic";

// Lazy loading des composants non-critiques
const AcademyStatsWidgetLazy = dynamic(
  () =>
    import("@/components/home/AcademyStatsWidget").then((mod) => ({
      default: mod.AcademyStatsWidget,
    })),
  {
    ssr: false,
    loading: () => (
      <Card className="border border-border/50 bg-card/40 backdrop-blur-md">
        <CardContent className="py-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="text-center space-y-2">
                <Skeleton className="h-8 w-8 mx-auto rounded-full" />
                <Skeleton className="h-6 w-12 mx-auto" />
                <Skeleton className="h-4 w-20 mx-auto" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    ),
  }
);

// Types
interface Feature {
  icon: React.ComponentType<{ className?: string }>;
  titleKey: string;
  descriptionKey: string;
}

/**
 * Page d'accueil Mathakine - Version optimisée
 */
export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const t = useTranslations("home");
  const { shouldReduceMotion } = useAccessibleAnimation();

  const features: Feature[] = [
    {
      icon: BookOpen,
      titleKey: "features.feature1.title",
      descriptionKey: "features.feature1.description",
    },
    {
      icon: Zap,
      titleKey: "features.feature2.title",
      descriptionKey: "features.feature2.description",
    },
    {
      icon: Trophy,
      titleKey: "features.feature3.title",
      descriptionKey: "features.feature3.description",
    },
    {
      icon: Users,
      titleKey: "features.feature4.title",
      descriptionKey: "features.feature4.description",
    },
  ];

  return (
    <PageLayout>
      {/* Hero Section */}
      <section className="text-center py-8 md:py-12 space-y-4" aria-labelledby="hero-title">
        <div
          id="hero-title"
          className={cn(
            "flex flex-col items-center",
            !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4"
          )}
        >
          <LogoBadge alt={t("hero.title")} className="mb-6" />
          <h1
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

        {/* CTAs — 2 boutons centrés */}
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

      {/* Stats de l'Académie */}
      <section className="py-4" aria-label="Statistiques de l'Académie">
        <AcademyStatsWidgetLazy />
      </section>

      {/* Fonctionnalités */}
      <section className="py-8 md:py-12 space-y-4" aria-labelledby="features-title">
        <div className="text-center space-y-2">
          <h2 id="features-title" className="text-2xl md:text-3xl font-bold">
            {t("features.title")}
          </h2>
          <p className="text-muted-foreground max-w-xl mx-auto text-sm">
            {t("features.description")}
          </p>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card
                key={feature.titleKey}
                className="bg-card/40 border border-border/50 backdrop-blur-md text-center p-6 md:p-8 cursor-default"
              >
                <CardHeader className="pb-2 pt-0 px-0">
                  <div className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
                  </div>
                  <CardTitle className="text-sm md:text-base">{t(feature.titleKey)}</CardTitle>
                </CardHeader>
                <CardContent className="pt-0 px-0">
                  <CardDescription className="text-xs md:text-sm">
                    {t(feature.descriptionKey)}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>
    </PageLayout>
  );
}
