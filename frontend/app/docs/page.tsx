"use client";

import Link from "next/link";
import {
  BookOpen,
  Shield,
  Zap,
  TrendingUp,
  UserPlus,
  Dumbbell,
  Puzzle,
  LayoutDashboard,
  Award,
  Accessibility,
  Coffee,
  PartyPopper,
  Sparkles,
  ChevronDown,
} from "lucide-react";
import { PageLayout, PageSection } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTranslations } from "next-intl";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { cn } from "@/lib/utils/cn";

/**
 * Page Documentation — Guide utilisateur intégré
 * Ton rassurant, valorisation des progrès, pas de pression.
 * Respect des principes psychologiques et rétention du GUIDE_UTILISATEUR_MVP.
 */
export default function DocsPage() {
  const t = useTranslations("docs");
  const { shouldReduceMotion } = useAccessibleAnimation();
  const faqItems = [
    { id: "q1", q: "q1", a: "a1" },
    { id: "q2", q: "q2", a: "a2" },
    { id: "q3", q: "q3", a: "a3" },
    { id: "q4", q: "q4", a: "a4" },
    { id: "q5", q: "q5", a: "a5" },
    { id: "q6", q: "q6", a: "a6" },
    { id: "q7", q: "q7", a: "a7" },
    { id: "q8", q: "q8", a: "a8" },
    { id: "q9", q: "q9", a: "a9" },
  ];

  return (
    <PageLayout maxWidth="2xl">
      {/* Hero — ton accueillant */}
      <header
        className={cn(
          "text-center py-8 md:py-12 space-y-4",
          !shouldReduceMotion && "animate-in fade-in duration-500"
        )}
      >
        <div className="flex justify-center">
          <div className="rounded-full bg-primary/10 p-4">
            <BookOpen className="h-12 w-12 text-primary" aria-hidden="true" />
          </div>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-foreground">{t("title")}</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">{t("subtitle")}</p>
      </header>

      {/* Pourquoi Mathakine — bienveillance */}
      <PageSection
        title={t("why.title")}
        description={t("why.intro")}
        icon={Sparkles}
        className="space-y-6"
      >
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card className="border-border bg-card/50">
            <CardContent className="pt-6 space-y-2">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" aria-hidden="true" />
                <span className="font-semibold">{t("why.safe")}</span>
              </div>
              <p className="text-sm text-muted-foreground">{t("why.safeDesc")}</p>
            </CardContent>
          </Card>
          <Card className="border-border bg-card/50">
            <CardContent className="pt-6 space-y-2">
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" aria-hidden="true" />
                <span className="font-semibold">{t("why.pace")}</span>
              </div>
              <p className="text-sm text-muted-foreground">{t("why.paceDesc")}</p>
            </CardContent>
          </Card>
          <Card className="border-border bg-card/50 sm:col-span-2 lg:col-span-1">
            <CardContent className="pt-6 space-y-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" aria-hidden="true" />
                <span className="font-semibold">{t("why.progress")}</span>
              </div>
              <p className="text-sm text-muted-foreground">{t("why.progressDesc")}</p>
            </CardContent>
          </Card>
        </div>
      </PageSection>

      {/* Démarrer — parcours simple */}
      <PageSection title={t("getStarted.title")} icon={UserPlus} className="space-y-4">
        <ol className="grid sm:grid-cols-3 gap-6 list-none">
          <li className="relative flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                1
              </span>
              <span className="font-semibold">{t("getStarted.step1")}</span>
            </div>
            <p className="text-sm text-muted-foreground pl-10">{t("getStarted.step1Desc")}</p>
          </li>
          <li className="relative flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                2
              </span>
              <span className="font-semibold">{t("getStarted.step2")}</span>
            </div>
            <p className="text-sm text-muted-foreground pl-10">{t("getStarted.step2Desc")}</p>
          </li>
          <li className="relative flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                3
              </span>
              <span className="font-semibold">{t("getStarted.step3")}</span>
            </div>
            <p className="text-sm text-muted-foreground pl-10">{t("getStarted.step3Desc")}</p>
          </li>
        </ol>
      </PageSection>

      {/* Utiliser Mathakine */}
      <PageSection title={t("using.title")} icon={Dumbbell} className="space-y-4">
        <div className="grid sm:grid-cols-2 gap-4">
          <Card>
            <CardContent className="pt-6 flex gap-4">
              <div className="rounded-lg bg-primary/10 p-3 h-fit">
                <Dumbbell className="h-6 w-6 text-primary" aria-hidden="true" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">{t("using.exercises")}</h3>
                <p className="text-sm text-muted-foreground">{t("using.exercisesDesc")}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 flex gap-4">
              <div className="rounded-lg bg-primary/10 p-3 h-fit">
                <Puzzle className="h-6 w-6 text-primary" aria-hidden="true" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">{t("using.challenges")}</h3>
                <p className="text-sm text-muted-foreground">{t("using.challengesDesc")}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 flex gap-4">
              <div className="rounded-lg bg-primary/10 p-3 h-fit">
                <LayoutDashboard className="h-6 w-6 text-primary" aria-hidden="true" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">{t("using.dashboard")}</h3>
                <p className="text-sm text-muted-foreground">{t("using.dashboardDesc")}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 flex gap-4">
              <div className="rounded-lg bg-primary/10 p-3 h-fit">
                <Award className="h-6 w-6 text-primary" aria-hidden="true" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">{t("using.badges")}</h3>
                <p className="text-sm text-muted-foreground">{t("using.badgesDesc")}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageSection>

      {/* Accessibilité — inclusivité */}
      <PageSection
        title={t("accessibility.title")}
        description={t("accessibility.intro")}
        icon={Accessibility}
      >
        <Card>
          <CardContent className="pt-6">
            <h3 className="font-semibold mb-2">{t("accessibility.where")}</h3>
            <p className="text-sm text-muted-foreground">{t("accessibility.whereDesc")}</p>
          </CardContent>
        </Card>
      </PageSection>

      {/* Rétention — conseils motivation */}
      <PageSection
        title={t("retention.title")}
        icon={PartyPopper}
        description=""
        className="space-y-4"
      >
        <div className="grid sm:grid-cols-3 gap-4">
          <Card className="border-primary/20">
            <CardContent className="pt-6 flex gap-3">
              <Coffee className="h-6 w-6 text-primary shrink-0" aria-hidden="true" />
              <div>
                <h3 className="font-semibold mb-1">{t("retention.short")}</h3>
                <p className="text-sm text-muted-foreground">{t("retention.shortDesc")}</p>
              </div>
            </CardContent>
          </Card>
          <Card className="border-primary/20">
            <CardContent className="pt-6 flex gap-3">
              <PartyPopper className="h-6 w-6 text-primary shrink-0" aria-hidden="true" />
              <div>
                <h3 className="font-semibold mb-1">{t("retention.celebrate")}</h3>
                <p className="text-sm text-muted-foreground">{t("retention.celebrateDesc")}</p>
              </div>
            </CardContent>
          </Card>
          <Card className="border-primary/20">
            <CardContent className="pt-6 flex gap-3">
              <Sparkles className="h-6 w-6 text-primary shrink-0" aria-hidden="true" />
              <div>
                <h3 className="font-semibold mb-1">{t("retention.choose")}</h3>
                <p className="text-sm text-muted-foreground">{t("retention.chooseDesc")}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageSection>

      {/* FAQ — accordion natif details/summary */}
      <PageSection title={t("faq.title")} icon={BookOpen} className="space-y-2">
        <div className="space-y-2">
          {faqItems.map((item) => (
            <details
              key={item.id}
              className="group rounded-lg border border-border bg-card [&[open]]:bg-muted/30"
            >
              <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-3 text-sm font-medium transition-colors hover:bg-muted/50 [&::-webkit-details-marker]:hidden">
                <span>{t(`faq.${item.q}`)}</span>
                <ChevronDown
                  className="h-4 w-4 shrink-0 transition-transform group-open:rotate-180"
                  aria-hidden="true"
                />
              </summary>
              <div className="border-t border-border px-4 py-3 text-sm text-muted-foreground">
                {t(`faq.${item.a}`)}
              </div>
            </details>
          ))}
        </div>
      </PageSection>

      {/* CTA — appel à l'action doux */}
      <section className="py-8 text-center space-y-6">
        <h2 className="text-xl font-semibold">{t("cta")}</h2>
        <div className="flex flex-wrap justify-center gap-3">
          <Button asChild variant="default" className="gap-2">
            <Link href="/exercises">
              <Dumbbell className="h-4 w-4" aria-hidden="true" />
              {t("ctaExercises")}
            </Link>
          </Button>
          <Button asChild variant="outline" className="gap-2">
            <Link href="/challenges">
              <Puzzle className="h-4 w-4" aria-hidden="true" />
              {t("ctaChallenges")}
            </Link>
          </Button>
          <Button asChild variant="secondary" className="gap-2">
            <Link href="/register">
              <UserPlus className="h-4 w-4" aria-hidden="true" />
              {t("ctaRegister")}
            </Link>
          </Button>
        </div>
      </section>
    </PageLayout>
  );
}
