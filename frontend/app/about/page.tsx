"use client";

import { Info, Target, Sparkles } from "lucide-react";
import Link from "next/link";
import { PageLayout, PageSection } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTranslations } from "next-intl";

export default function AboutPage() {
  const t = useTranslations("about");

  return (
    <PageLayout maxWidth="2xl">
      <header className="text-center py-8 md:py-12 space-y-4">
        <div className="flex justify-center">
          <div className="rounded-full bg-primary/10 p-4">
            <Info className="h-12 w-12 text-primary" aria-hidden="true" />
          </div>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-foreground">{t("title")}</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">{t("subtitle")}</p>
      </header>

      <PageSection title={t("what.title")} description={t("what.intro")}>
        <Card>
          <CardContent className="pt-6 space-y-4">
            <p className="text-muted-foreground">{t("what.desc")}</p>
            <ul className="list-disc list-inside space-y-2 text-muted-foreground">
              <li>{t("what.bullet1")}</li>
              <li>{t("what.bullet2")}</li>
              <li>{t("what.bullet3")}</li>
            </ul>
          </CardContent>
        </Card>
      </PageSection>

      <PageSection title={t("origin.title")} description={t("origin.intro")}>
        <div className="space-y-4">
          <Card className="border-l-4 border-l-primary/50">
            <CardContent className="pt-6 flex gap-4">
              <div className="shrink-0 rounded-lg bg-primary/10 p-3 h-fit">
                <Target className="h-6 w-6 text-primary" aria-hidden="true" />
              </div>
              <div className="space-y-3">
                <p className="text-muted-foreground">{t("origin.p1")}</p>
                <p className="text-muted-foreground">{t("origin.p2")}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 space-y-3">
              <p className="text-muted-foreground">{t("origin.p3")}</p>
              <p className="text-muted-foreground">{t("origin.p4")}</p>
            </CardContent>
          </Card>

          <div className="flex items-center gap-3 rounded-lg border border-primary/20 bg-primary/5 px-4 py-3">
            <Sparkles className="h-5 w-5 shrink-0 text-primary" aria-hidden="true" />
            <p className="text-sm font-medium text-foreground italic">{t("origin.tagline")}</p>
          </div>
        </div>
      </PageSection>

      <PageSection title={t("who.title")} description={t("who.intro")}>
        <Card>
          <CardContent className="pt-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <p className="text-muted-foreground">{t("who.desc")}</p>
            <Button asChild variant="outline" size="sm">
              <Link href="/contact">{t("contactCta")}</Link>
            </Button>
          </CardContent>
        </Card>
      </PageSection>
    </PageLayout>
  );
}
