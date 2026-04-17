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
  Settings,
  ListTodo,
  ChevronRight,
  MessageCircleQuestion,
  Heart,
  Flag,
  Brain,
  AlertTriangle,
  Info,
} from "lucide-react";
import { getTranslations } from "next-intl/server";
import { PageLayout, PageSection } from "@/components/layout";
import { Button } from "@/components/ui/button";

const SECTION_HEADER_ICON_CLASS = "h-5 w-5 text-primary";

const QUICKSTART_STEPS = [
  { step: 1, icon: UserPlus, href: "/register" },
  { step: 2, icon: Brain, href: "/diagnostic" },
  { step: 3, icon: Dumbbell, href: "/exercises" },
  { step: 4, icon: Puzzle, href: "/challenges" },
  { step: 5, icon: Settings, href: "/settings" },
] as const;

const REPORT_ENTRIES = [
  { key: "entry1", icon: Flag },
  { key: "entry2", icon: Dumbbell },
  { key: "entry3", icon: Puzzle },
  { key: "entry4", icon: Flag },
] as const;

export default async function DocsPage() {
  const t = await getTranslations("docs");

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
    { id: "q10", q: "q10", a: "a10" },
    { id: "q11", q: "q11", a: "a11" },
  ];

  const whyItems = [
    { key: "safe", icon: Shield },
    { key: "pace", icon: Zap },
    { key: "progress", icon: TrendingUp },
  ] as const;

  const usingItems = [
    { key: "exercises", icon: Dumbbell },
    { key: "challenges", icon: Puzzle },
    { key: "dashboard", icon: LayoutDashboard },
    { key: "badges", icon: Award },
  ] as const;

  const retentionItems = [
    { key: "short", icon: Coffee },
    { key: "celebrate", icon: PartyPopper },
    { key: "choose", icon: Sparkles },
  ] as const;

  const betaExpectItems: string[] = [0, 1, 2, 3, 4, 5].map((i) => t(`betaExpect.items.${i}`));
  const betaLimitItems: string[] = [0, 1, 2].map((i) => t(`betaLimits.items.${i}`));

  return (
    <PageLayout maxWidth="2xl">
      {/* 1. Hero — beta-oriented */}
      <header className="text-center py-12 md:py-16 space-y-4 motion-safe:animate-in motion-safe:fade-in motion-safe:duration-500">
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/20 rounded-2xl blur-xl" />
            <div className="relative bg-card border border-border/50 p-4 rounded-2xl shadow-sm">
              <BookOpen className="h-10 w-10 text-primary" aria-hidden="true" />
            </div>
          </div>
        </div>
        <h1 className="text-3xl md:text-5xl font-bold text-foreground">{t("betaHero.title")}</h1>
        <p className="text-lg md:text-xl text-primary font-medium">{t("betaHero.subtitle")}</p>
        <div className="flex flex-col sm:flex-row justify-center items-center gap-3 pt-4">
          <Button asChild size="lg" className="w-full sm:w-auto gap-2 group">
            <Link href="/register">
              <UserPlus className="h-5 w-5" aria-hidden="true" />
              {t("betaHero.ctaRegister")}
              <ChevronRight
                className="h-4 w-4 -mr-1 group-hover:translate-x-1 transition-transform"
                aria-hidden="true"
              />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="w-full sm:w-auto gap-2">
            <Link href="/exercises">
              <Dumbbell className="h-5 w-5 text-primary" aria-hidden="true" />
              {t("betaHero.ctaExercises")}
            </Link>
          </Button>
        </div>
      </header>

      <div className="space-y-12 md:space-y-16">
        {/* 2. Quickstart — 5 steps */}
        <PageSection
          title={t("quickstart.title")}
          description={t("quickstart.intro")}
          icon={<ListTodo className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="bg-card/80 border border-border backdrop-blur-md p-6 md:p-8 rounded-2xl space-y-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 -mt-16 -mr-16 w-32 h-32 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
            <div className="space-y-5 relative z-10">
              {QUICKSTART_STEPS.map(({ step, icon: Icon, href }) => (
                <div key={step} className="flex items-start gap-4">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary text-sm font-bold ring-1 ring-primary/20">
                    {step}
                  </span>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-foreground">{t(`quickstart.step${step}`)}</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed mt-0.5">
                      {t(`quickstart.step${step}Desc`)}
                    </p>
                  </div>
                  <Button asChild variant="outline" size="sm" className="shrink-0 hidden sm:flex">
                    <Link href={href}>
                      <Icon className="h-4 w-4 mr-1.5" aria-hidden="true" />
                      {t(`quickstart.step${step}Cta`)}
                    </Link>
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </PageSection>

        {/* 3. Beta expectations */}
        <PageSection
          title={t("betaExpect.title")}
          description={t("betaExpect.intro")}
          icon={<AlertTriangle className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {betaExpectItems.map((item, i) => (
              <div
                key={i}
                className="bg-muted/30 border border-border/50 p-4 rounded-xl text-sm text-foreground"
              >
                {item}
              </div>
            ))}
          </div>
        </PageSection>

        {/* 4. How to report */}
        <PageSection
          title={t("howToReport.title")}
          description={t("howToReport.intro")}
          icon={<Flag className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="bg-card/50 border border-border rounded-2xl p-6 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {REPORT_ENTRIES.map(({ key, icon: Icon }) => (
                <div
                  key={key}
                  className="flex items-center gap-3 bg-muted/20 border border-border/50 p-3 rounded-xl text-sm"
                >
                  <Icon className="h-4 w-4 text-primary shrink-0" aria-hidden="true" />
                  <span className="text-foreground">{t(`howToReport.${key}`)}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground italic">{t("howToReport.note")}</p>
          </div>
        </PageSection>

        {/* 5. Beta limits */}
        <PageSection
          title={t("betaLimits.title")}
          description={t("betaLimits.intro")}
          icon={<Info className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="bg-muted/20 border border-border/50 p-6 rounded-2xl space-y-3">
            {betaLimitItems.map((item, i) => (
              <div key={i} className="flex items-start gap-3 text-sm text-muted-foreground">
                <span className="text-primary mt-0.5">—</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-4">{t("betaGuideLink")}</p>
        </PageSection>

        {/* 6. Pourquoi Mathakine */}
        <PageSection
          title={t("why.title")}
          description={t("why.intro")}
          icon={<Sparkles className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {whyItems.map(({ key, icon: Icon }) => (
              <div
                key={key}
                className="bg-muted/30 border border-border/50 p-5 rounded-xl flex flex-col gap-3 transition-all hover:bg-muted/50 hover:border-primary/20"
              >
                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
                </div>
                <h3 className="font-semibold text-foreground">{t(`why.${key}`)}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {t(`why.${key}Desc`)}
                </p>
              </div>
            ))}
          </div>
        </PageSection>

        {/* 7. Utiliser Mathakine */}
        <PageSection
          title={t("using.title")}
          icon={<ListTodo className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {usingItems.map(({ key, icon: Icon }) => (
              <div
                key={key}
                className="bg-card/50 border border-border p-5 md:p-6 rounded-xl flex gap-4 transition-all hover:bg-card hover:shadow-sm hover:border-primary/20"
              >
                <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Icon className="h-6 w-6 text-primary" aria-hidden="true" />
                </div>
                <div className="space-y-1.5 flex-1 min-w-0">
                  <h3 className="font-semibold text-foreground">{t(`using.${key}`)}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {t(`using.${key}Desc`)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </PageSection>

        {/* 8. Accessibilité */}
        <PageSection
          title={t("accessibility.title")}
          icon={<Accessibility className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="border border-primary/30 bg-primary/5 p-6 md:p-8 rounded-2xl space-y-4">
            <p className="text-foreground font-medium leading-relaxed">
              {t("accessibility.intro")}
            </p>
            <div className="pt-3 border-t border-primary/10 mt-4">
              <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                <Settings className="h-4 w-4 text-primary" aria-hidden="true" />
                {t("accessibility.where")}
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {t("accessibility.whereDesc")}
              </p>
            </div>
          </div>
        </PageSection>

        {/* 9. Rétention / Motivation */}
        <PageSection
          title={t("retention.title")}
          icon={<Heart className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {retentionItems.map(({ key, icon: Icon }) => (
              <div
                key={key}
                className="bg-muted/20 border border-border/50 p-5 rounded-xl flex flex-col gap-3 transition-colors hover:bg-muted/40"
              >
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-primary shrink-0" aria-hidden="true" />
                  <h3 className="font-semibold text-foreground">{t(`retention.${key}`)}</h3>
                </div>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {t(`retention.${key}Desc`)}
                </p>
              </div>
            ))}
          </div>
        </PageSection>

        {/* 10. FAQ */}
        <PageSection
          title={t("faq.title")}
          icon={<MessageCircleQuestion className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="bg-card/50 border border-border rounded-2xl overflow-hidden divide-y divide-border">
            {faqItems.map((item) => (
              <details
                key={item.id}
                id={`faq-${item.id}`}
                className="group [&_summary::-webkit-details-marker]:hidden"
              >
                <summary className="flex cursor-pointer list-none items-center justify-between p-5 text-sm md:text-base font-medium text-foreground transition-colors hover:bg-muted/50 focus-visible:outline-none focus-visible:bg-muted/50 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-inset">
                  <span>{t(`faq.${item.q}`)}</span>
                  <div className="ml-4 flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full border border-border/50 group-open:bg-primary/10 group-open:border-primary/20 transition-all">
                    <ChevronDown
                      className="h-4 w-4 text-muted-foreground group-open:text-primary transition-transform duration-300 group-open:rotate-180"
                      aria-hidden="true"
                    />
                  </div>
                </summary>
                <div className="px-5 pb-5 text-sm text-muted-foreground leading-relaxed animate-in slide-in-from-top-1 fade-in duration-200">
                  {t(`faq.${item.a}`)}
                </div>
              </details>
            ))}
          </div>
        </PageSection>

        {/* 11. CTA final */}
        <section className="py-8 md:py-12 text-center space-y-8 border-t border-border">
          <h2 className="text-xl md:text-2xl font-semibold text-foreground">{t("cta")}</h2>
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
            <Button asChild size="lg" className="w-full sm:w-auto gap-2 group">
              <Link href="/exercises">
                <Dumbbell className="h-5 w-5" aria-hidden="true" />
                {t("ctaExercises")}
                <ChevronRight
                  className="h-4 w-4 -mr-1 group-hover:translate-x-1 transition-transform"
                  aria-hidden="true"
                />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="w-full sm:w-auto gap-2">
              <Link href="/challenges">
                <Puzzle className="h-5 w-5 text-primary" aria-hidden="true" />
                {t("ctaChallenges")}
              </Link>
            </Button>
            <Button asChild variant="secondary" size="lg" className="w-full sm:w-auto gap-2">
              <Link href="/register">
                <UserPlus className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                {t("ctaRegister")}
              </Link>
            </Button>
          </div>
        </section>
      </div>
    </PageLayout>
  );
}
