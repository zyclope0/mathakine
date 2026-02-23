"use client";

import { Shield } from "lucide-react";
import { PageLayout, PageSection } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { useTranslations } from "next-intl";

export default function PrivacyPage() {
  const t = useTranslations("privacy");

  return (
    <PageLayout maxWidth="2xl">
      <header className="text-center py-8 md:py-12 space-y-4">
        <div className="flex justify-center">
          <div className="rounded-full bg-primary/10 p-4">
            <Shield className="h-12 w-12 text-primary" aria-hidden="true" />
          </div>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-foreground">{t("title")}</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">{t("subtitle")}</p>
        <p className="text-sm text-muted-foreground">{t("lastUpdate")}</p>
      </header>

      <PageSection title={t("controller.title")} description={t("controller.desc")}>
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">{t("controller.text")}</p>
          </CardContent>
        </Card>
      </PageSection>

      <PageSection title={t("data.title")} description={t("data.intro")}>
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div>
              <h3 className="font-semibold mb-1">{t("data.account.title")}</h3>
              <p className="text-sm text-muted-foreground">{t("data.account.desc")}</p>
            </div>
            <div>
              <h3 className="font-semibold mb-1">{t("data.progress.title")}</h3>
              <p className="text-sm text-muted-foreground">{t("data.progress.desc")}</p>
            </div>
            <div>
              <h3 className="font-semibold mb-1">{t("data.feedback.title")}</h3>
              <p className="text-sm text-muted-foreground">{t("data.feedback.desc")}</p>
            </div>
            <div>
              <h3 className="font-semibold mb-1">{t("data.technical.title")}</h3>
              <p className="text-sm text-muted-foreground">{t("data.technical.desc")}</p>
            </div>
          </CardContent>
        </Card>
      </PageSection>

      <PageSection title={t("retention.title")} description={t("retention.intro")}>
        <Card>
          <CardContent className="pt-6 space-y-2">
            <p className="text-muted-foreground">{t("retention.account")}</p>
            <p className="text-muted-foreground">{t("retention.progress")}</p>
            <p className="text-muted-foreground">{t("retention.feedback")}</p>
            <p className="text-muted-foreground">{t("retention.logs")}</p>
          </CardContent>
        </Card>
      </PageSection>

      <PageSection title={t("rights.title")} description={t("rights.intro")}>
        <Card>
          <CardContent className="pt-6">
            <ul className="list-disc list-inside space-y-2 text-muted-foreground">
              <li>{t("rights.access")}</li>
              <li>{t("rights.rectification")}</li>
              <li>{t("rights.erasure")}</li>
              <li>{t("rights.portability")}</li>
              <li>{t("rights.objection")}</li>
              <li>{t("rights.complaint")}</li>
            </ul>
          </CardContent>
        </Card>
      </PageSection>

      <PageSection title={t("subcontractors.title")} description={t("subcontractors.intro")}>
        <Card>
          <CardContent className="pt-6 space-y-4">
            <p className="text-muted-foreground">{t("subcontractors.note")}</p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li>{t("subcontractors.render")}</li>
              <li>{t("subcontractors.sentry")}</li>
              <li>{t("subcontractors.email")}</li>
            </ul>
          </CardContent>
        </Card>
      </PageSection>

      <PageSection title={t("cookies.title")} description={t("cookies.intro")}>
        <Card>
          <CardContent className="pt-6 space-y-4">
            <p className="text-muted-foreground">{t("cookies.essential")}</p>
            <p className="text-sm text-muted-foreground">{t("cookies.noMarketing")}</p>
          </CardContent>
        </Card>
      </PageSection>
    </PageLayout>
  );
}
