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
      <header className="space-y-5 py-10 text-center md:space-y-6 md:py-14">
        <div className="mb-2 flex justify-center md:mb-3">
          <div className="rounded-2xl border border-border/60 bg-card/90 p-4 ring-1 ring-primary/15">
            <BookOpen className="h-10 w-10 text-primary" aria-hidden="true" />
          </div>
        </div>
        <h1 className="text-balance text-3xl font-bold tracking-tight text-foreground md:text-5xl">
          {t("betaHero.title")}
        </h1>
        <p className="mx-auto max-w-[42ch] text-pretty text-lg font-medium text-primary md:max-w-[48ch] md:text-xl">
          {t("betaHero.subtitle")}
        </p>
        <div className="flex flex-col items-center justify-center gap-3 pt-2 sm:flex-row sm:pt-3">
          <Button asChild size="lg" className="group w-full gap-2 sm:w-auto min-h-11">
            <Link href="/register">
              <UserPlus className="h-5 w-5" aria-hidden="true" />
              {t("betaHero.ctaRegister")}
              <ChevronRight
                className="-mr-1 h-4 w-4 transition-transform group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="w-full gap-2 sm:w-auto min-h-11">
            <Link href="/exercises">
              <Dumbbell className="h-5 w-5 text-primary" aria-hidden="true" />
              {t("betaHero.ctaExercises")}
            </Link>
          </Button>
        </div>
      </header>

      <div className="space-y-14 md:space-y-20">
        {/* 2. Quickstart — 5 steps */}
        <PageSection
          title={t("quickstart.title")}
          description={t("quickstart.intro")}
          icon={<ListTodo className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="overflow-hidden rounded-2xl border border-border/60 bg-card/90">
            <div className="divide-y divide-border/50">
              {QUICKSTART_STEPS.map(({ step, icon: Icon, href }) => (
                <div key={step} className="flex items-start gap-4 px-4 py-5 sm:px-6 sm:py-6">
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary ring-1 ring-primary/15">
                    {step}
                  </span>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-foreground">{t(`quickstart.step${step}`)}</h3>
                    <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                      {t(`quickstart.step${step}Desc`)}
                    </p>
                  </div>
                  <Button
                    asChild
                    variant="outline"
                    size="sm"
                    className="hidden min-h-9 shrink-0 sm:flex"
                  >
                    <Link href={href}>
                      <Icon className="mr-1.5 h-4 w-4" aria-hidden="true" />
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
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3 md:gap-4">
            {betaExpectItems.map((item, i) => (
              <div
                key={i}
                className="rounded-xl bg-muted/20 p-4 text-sm leading-snug text-foreground ring-1 ring-border/40"
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
          <div className="space-y-5 rounded-2xl border border-border/60 bg-muted/10 p-6 md:p-7">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4">
              {REPORT_ENTRIES.map(({ key, icon: Icon }) => (
                <div
                  key={key}
                  className="flex items-start gap-3 rounded-xl bg-card/70 p-3.5 text-sm ring-1 ring-border/40 sm:items-center"
                >
                  <Icon
                    className="mt-0.5 h-4 w-4 shrink-0 text-primary sm:mt-0"
                    aria-hidden="true"
                  />
                  <span className="text-pretty text-foreground">{t(`howToReport.${key}`)}</span>
                </div>
              ))}
            </div>
            <p className="text-xs leading-relaxed text-muted-foreground">{t("howToReport.note")}</p>
          </div>
        </PageSection>

        {/* 5. Beta limits */}
        <PageSection
          title={t("betaLimits.title")}
          description={t("betaLimits.intro")}
          icon={<Info className={SECTION_HEADER_ICON_CLASS} aria-hidden />}
        >
          <div className="space-y-4 rounded-2xl bg-muted/15 p-6 ring-1 ring-border/40 md:p-7">
            {betaLimitItems.map((item, i) => (
              <div key={i} className="flex gap-3 text-sm leading-relaxed text-muted-foreground">
                <span
                  className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/40"
                  aria-hidden="true"
                />
                <span>{item}</span>
              </div>
            ))}
          </div>
          <div className="mt-5 rounded-xl bg-card/80 p-4 ring-1 ring-border/50 md:p-5">
            <p className="text-sm font-semibold text-foreground">{t("betaGuideNoteTitle")}</p>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              {t("betaGuideLink")}
            </p>
          </div>
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
                className="flex flex-col gap-3 rounded-xl bg-muted/25 p-5 ring-1 ring-border/40 transition-colors hover:bg-muted/40"
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
                className="flex gap-4 rounded-xl bg-card/60 p-5 ring-1 ring-border/50 transition-colors hover:bg-card/80 md:p-6"
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
          <div className="space-y-4 rounded-2xl border border-primary/25 bg-primary/5 p-6 md:p-8">
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
          <div className="divide-y divide-border/60 overflow-hidden rounded-2xl border border-border/60 bg-card/40">
            {faqItems.map((item) => (
              <details
                key={item.id}
                id={`faq-${item.id}`}
                className="group [&_summary::-webkit-details-marker]:hidden"
              >
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-4 text-sm font-medium text-foreground transition-colors hover:bg-muted/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background md:p-5 md:text-base">
                  <span className="text-pretty text-left">{t(`faq.${item.q}`)}</span>
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-border/50 bg-muted/20 group-open:border-primary/25 group-open:bg-primary/10">
                    <ChevronDown
                      className="h-4 w-4 text-muted-foreground transition-transform duration-200 group-open:rotate-180 group-open:text-primary motion-reduce:transition-none"
                      aria-hidden="true"
                    />
                  </div>
                </summary>
                <div className="border-t border-border/40 bg-muted/10 px-4 pb-4 pt-0 text-sm leading-relaxed text-muted-foreground md:px-5 md:pb-5">
                  <div className="pt-3">{t(`faq.${item.a}`)}</div>
                </div>
              </details>
            ))}
          </div>
        </PageSection>

        {/* 11. CTA final */}
        <section className="rounded-2xl bg-muted/20 px-4 py-10 text-center ring-1 ring-border/50 md:px-8 md:py-12">
          <div className="mx-auto max-w-2xl space-y-6 md:space-y-8">
            <h2 className="text-balance text-xl font-semibold tracking-tight text-foreground md:text-2xl">
              {t("cta")}
            </h2>
            <div className="flex flex-col items-center justify-center gap-3 sm:flex-row sm:flex-wrap sm:gap-4">
              <Button asChild size="lg" className="group w-full gap-2 sm:w-auto min-h-11">
                <Link href="/exercises">
                  <Dumbbell className="h-5 w-5" aria-hidden="true" />
                  {t("ctaExercises")}
                  <ChevronRight
                    className="-mr-1 h-4 w-4 transition-transform group-hover:translate-x-0.5"
                    aria-hidden="true"
                  />
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="w-full gap-2 sm:w-auto min-h-11"
              >
                <Link href="/challenges">
                  <Puzzle className="h-5 w-5 text-primary" aria-hidden="true" />
                  {t("ctaChallenges")}
                </Link>
              </Button>
              <Button
                asChild
                variant="secondary"
                size="lg"
                className="w-full gap-2 sm:w-auto min-h-11"
              >
                <Link href="/register">
                  <UserPlus className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                  {t("ctaRegister")}
                </Link>
              </Button>
            </div>
          </div>
        </section>
      </div>
    </PageLayout>
  );
}
