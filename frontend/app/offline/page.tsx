"use client";

import { Button } from "@/components/ui/button";
import { WifiOff, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

export default function OfflinePage() {
  const router = useRouter();
  const t = useTranslations("offline");

  const handleRetry = () => {
    if (navigator.onLine) {
      router.refresh();
    } else {
      window.addEventListener(
        "online",
        () => {
          router.refresh();
        },
        { once: true }
      );
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="text-center space-y-6 max-w-md">
        <div className="flex justify-center">
          <div className="rounded-full bg-muted p-6">
            <WifiOff className="h-16 w-16 text-muted-foreground" />
          </div>
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl font-bold">{t("title")}</h1>
          <p className="text-muted-foreground">{t("body")}</p>
        </div>

        <Button onClick={handleRetry} className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          {t("retry")}
        </Button>

        <p className="text-sm text-muted-foreground">{t("footer")}</p>
      </div>
    </div>
  );
}
