"use client";

import {
  Moon,
  Sigma,
  Heart,
  RefreshCcw,
  Mail,
} from "lucide-react";
import Link from "next/link";
import { PageLayout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { useTranslations } from "next-intl";

export default function AboutPage() {
  const t = useTranslations("about");

  const philosophyItems = [
    { key: "philosophy1", icon: Moon },
    { key: "philosophy2", icon: Sigma },
    { key: "philosophy3", icon: Heart },
    { key: "philosophy4", icon: RefreshCcw },
  ] as const;

  return (
    <PageLayout maxWidth="2xl">
      {/* 1. En-tête (Hero Section) */}
      <header className="text-center py-12 md:py-16 space-y-4">
        <h1 className="text-3xl md:text-5xl font-bold text-foreground">
          {t("title")}
        </h1>
        <p className="text-lg md:text-xl text-primary font-medium">
          {t("subtitle")}
        </p>
      </header>

      <div className="space-y-12 md:space-y-16">
        {/* 2. Section 1 : Une histoire née de la nécessité */}
        <section>
          <h2 className="text-xl md:text-2xl font-semibold text-foreground mb-6">
            {t("story.title")}
          </h2>
          <div className="bg-card/80 border border-border backdrop-blur-md p-6 md:p-8 rounded-2xl space-y-6">
            <p className="text-muted-foreground leading-relaxed">
              {t("story.p1")}
            </p>
            <p className="text-muted-foreground leading-relaxed">
              {t.rich("story.p2", {
                bold: (chunks) => (
                  <span className="font-semibold text-foreground">{chunks}</span>
                ),
              })}
            </p>
            <p className="text-muted-foreground leading-relaxed">
              {t("story.p3")}
            </p>
            <p className="text-muted-foreground leading-relaxed">
              {t("story.p4")}
            </p>
          </div>
        </section>

        {/* 3. Section 2 : La philosophie "Zéro Bruit" (Grille Bento) */}
        <section>
          <h2 className="text-xl md:text-2xl font-semibold text-foreground mb-2">
            {t("philosophy.title")}
          </h2>
          <p className="text-muted-foreground mb-6">
            {t("philosophy.intro")}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            {philosophyItems.map(({ key, icon: Icon }) => (
              <div
                key={key}
                className="bg-muted/30 border border-border/50 p-5 rounded-xl flex flex-col gap-2 transition-all hover:bg-muted/50"
              >
                <div className="flex items-center gap-3">
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
                  </div>
                  <h3 className="font-semibold text-foreground">
                    {t(`philosophy.${key}.title`)}
                  </h3>
                </div>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {t(`philosophy.${key}.desc`)}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* 4. Section 3 : L'effet "Bateau de trottoir" */}
        <section>
          <h2 className="text-xl md:text-2xl font-semibold text-foreground mb-6">
            {t("curb.title")}
          </h2>
          <div className="border-l-4 border-l-primary bg-primary/5 p-6 md:p-8 rounded-r-2xl space-y-6">
            <p className="text-muted-foreground leading-relaxed">
              {t("curb.p1")}
            </p>
            <p className="text-muted-foreground leading-relaxed font-medium">
              {t("curb.p2")}
            </p>
            <p className="text-muted-foreground leading-relaxed">
              {t("curb.p3")}
            </p>
          </div>
        </section>

        {/* 5. Section 4 : Une démarche transparente (Footer de la page) */}
        <section>
          <h2 className="text-xl md:text-2xl font-semibold text-foreground mb-6">
            {t("transparency.title")}
          </h2>
          <div className="bg-card/80 border border-border backdrop-blur-md p-6 md:p-8 rounded-2xl space-y-6">
            <p className="text-muted-foreground leading-relaxed">
              {t("transparency.p1")}
            </p>
            <p className="text-muted-foreground leading-relaxed">
              {t("transparency.p2")}
            </p>
            <p className="text-muted-foreground leading-relaxed">
              {t("transparency.p3")}
            </p>
            <p className="text-muted-foreground leading-relaxed">
              {t("transparency.p4")}
            </p>

            {/* Footer auteur */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pt-6 border-t border-border">
              <p className="text-sm font-medium text-foreground">
                {t("transparency.signature")}
              </p>
              <Button asChild variant="outline" size="sm">
                <Link href="/contact" className="flex items-center gap-2">
                  <Mail className="h-4 w-4" aria-hidden="true" />
                  {t("contactCta")}
                </Link>
              </Button>
            </div>
          </div>
        </section>
      </div>
    </PageLayout>
  );
}
