"use client";

import {
  Sparkles,
  Rocket,
  Calendar,
  Plus,
  Wrench,
  Zap,
  CheckCircle2,
} from "lucide-react";
import { PageLayout } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { cn } from "@/lib/utils/cn";

type VersionBlock = {
  version: string;
  date: string;
  items: string[];
};

const LATEST_KEY = "v222";

export default function ChangelogPage() {
  const t = useTranslations("changelog");
  const { shouldReduceMotion, createVariants, createTransition } =
    useAccessibleAnimation();

  const versionKeys = ["v222", "v221", "v220"] as const;

  const itemIcon = (idx: number, isLatest: boolean) => {
    if (!isLatest) return <CheckCircle2 className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden />;
    // Pour la dernière version : alterner icônes selon le type (nouveau / correctif / amélioration)
    const icons = [Plus, Zap, Wrench];
    const Icon = icons[idx % icons.length];
    return <Icon className="h-4 w-4 shrink-0 text-primary" aria-hidden />;
  };

  return (
    <PageLayout maxWidth="2xl">
      <header className="text-center py-8 md:py-12 space-y-4">
        <motion.div
          className="flex justify-center"
          {...(shouldReduceMotion
            ? {}
            : {
                initial: { opacity: 0, scale: 0.9 },
                animate: { opacity: 1, scale: 1 },
                transition: createTransition({ duration: 0.4 }),
              })}
        >
          <div className="rounded-full bg-gradient-to-br from-primary/20 to-accent/20 p-5 ring-2 ring-primary/30">
            <Sparkles
              className="h-14 w-14 text-primary"
              aria-hidden="true"
            />
          </div>
        </motion.div>
        <h1 className="text-3xl md:text-4xl font-bold text-foreground">
          {t("title")}
        </h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          {t("subtitle")}
        </p>
      </header>

      {/* Timeline */}
      <div className="relative">
        {/* Ligne verticale (desktop) */}
        <div
          className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-primary/40 via-primary/20 to-transparent hidden md:block"
          aria-hidden="true"
        />

        <div className="space-y-6">
          {versionKeys.map((key, idx) => {
            const block = t.raw(key) as VersionBlock | undefined;
            if (!block?.items?.length) return null;

            const isLatest = key === LATEST_KEY;

            return (
              <motion.article
                key={key}
                className="relative flex gap-6 md:gap-8"
                variants={createVariants({
                  initial: { opacity: 0, y: 16 },
                  animate: { opacity: 1, y: 0 },
                  exit: { opacity: 0 },
                })}
                initial="initial"
                animate="animate"
                transition={createTransition({
                  duration: 0.35,
                  delay: idx * 0.08,
                })}
              >
                {/* Point sur la timeline */}
                <div
                  className={cn(
                    "relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border-2 md:ml-0",
                    isLatest
                      ? "border-primary bg-primary/15"
                      : "border-muted bg-muted/50"
                  )}
                  aria-hidden="true"
                >
                  {isLatest ? (
                    <Rocket className="h-5 w-5 text-primary" />
                  ) : (
                    <Calendar className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>

                <div className="min-w-0 flex-1 pb-2">
                  {/* En-tête version */}
                  <div className="mb-3 flex flex-wrap items-center gap-2">
                    <h2 className="text-lg font-semibold text-foreground">
                      {block.version}
                    </h2>
                    {isLatest && (
                      <Badge
                        variant="default"
                        className="gap-1 text-xs"
                        aria-label={t("latestLabel")}
                      >
                        <Sparkles className="h-3 w-3" aria-hidden />
                        {t("latestBadge")}
                      </Badge>
                    )}
                    <span
                      className="text-sm text-muted-foreground"
                      aria-label={`Date : ${block.date}`}
                    >
                      {block.date}
                    </span>
                  </div>

                  {/* Carte des changements */}
                  <Card
                    className={cn(
                      "transition-colors",
                      isLatest
                        ? "border-primary/30 bg-primary/5 shadow-sm"
                        : "border-border"
                    )}
                  >
                    <CardContent className="pt-4 pb-4">
                      <ul className="space-y-3" role="list">
                        {block.items.map((item, itemIdx) => (
                          <li
                            key={itemIdx}
                            className="flex gap-3 items-start text-muted-foreground"
                          >
                            {itemIcon(itemIdx, isLatest)}
                            <span
                              className={cn(
                                "pt-0.5",
                                isLatest && "text-foreground/90"
                              )}
                            >
                              {item}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </div>
              </motion.article>
            );
          })}
        </div>
      </div>

      <div className="mt-10 flex justify-center">
        <p
          className="text-sm text-muted-foreground flex items-center gap-2 rounded-lg border border-border bg-muted/30 px-4 py-3"
          role="status"
        >
          <Sparkles className="h-4 w-4 shrink-0 text-primary" aria-hidden />
          {t("alphaNote")}
        </p>
      </div>
    </PageLayout>
  );
}
