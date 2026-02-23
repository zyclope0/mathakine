"use client";

import { useState } from "react";
import { Mail, MessageSquare, Send } from "lucide-react";
import Link from "next/link";
import { PageLayout, PageSection } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useTranslations } from "next-intl";

const CONTACT_EMAIL =
  process.env.NEXT_PUBLIC_CONTACT_EMAIL ||
  process.env.NEXT_PUBLIC_FEEDBACK_EMAIL ||
  "webmaster@mathakine.fun";

export default function ContactPage() {
  const t = useTranslations("contact");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const body = [name && `Nom : ${name}`, email && `Email : ${email}`, "", message]
      .filter(Boolean)
      .join("\n");
    const mailto = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject || "Contact Mathakine")}&body=${encodeURIComponent(body)}`;
    window.location.href = mailto;
  };

  return (
    <PageLayout maxWidth="2xl">
      <header className="text-center py-8 md:py-12 space-y-4">
        <div className="flex justify-center">
          <div className="rounded-full bg-primary/10 p-4">
            <Mail className="h-12 w-12 text-primary" aria-hidden="true" />
          </div>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-foreground">{t("title")}</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">{t("subtitle")}</p>
        <p className="text-sm text-muted-foreground">{t("responseTime")}</p>
      </header>

      <PageSection title={t("form.title")} description={t("form.intro")}>
        <Card>
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="contact-name">{t("form.name")}</Label>
                  <Input
                    id="contact-name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={t("form.namePlaceholder")}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="contact-email">{t("form.email")}</Label>
                  <Input
                    id="contact-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={t("form.emailPlaceholder")}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="contact-subject">{t("form.subject")}</Label>
                <Input
                  id="contact-subject"
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder={t("form.subjectPlaceholder")}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="contact-message">{t("form.message")}</Label>
                <Textarea
                  id="contact-message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder={t("form.messagePlaceholder")}
                  rows={5}
                  required
                />
              </div>
              <Button type="submit" className="gap-2">
                <Send className="h-4 w-4" aria-hidden="true" />
                {t("form.submit")}
              </Button>
            </form>
          </CardContent>
        </Card>
      </PageSection>

      <PageSection
        title={t("feedback.title")}
        description={t("feedback.intro")}
        icon={MessageSquare}
      >
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground mb-4">{t("feedback.desc")}</p>
            <Button asChild>
              <Link href="/exercises">{t("feedback.cta")}</Link>
            </Button>
          </CardContent>
        </Card>
      </PageSection>
    </PageLayout>
  );
}
