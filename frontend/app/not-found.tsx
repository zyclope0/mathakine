import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Home, Search } from "lucide-react";
import Link from "next/link";
import { useTranslations } from "next-intl";

export default function NotFound() {
  const t = useTranslations("errors.404");

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <Search className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
          </div>
          <CardTitle className="text-2xl">{t("title")}</CardTitle>
          <CardDescription className="text-base">{t("message")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-2 sm:flex-row">
            <Button asChild variant="default" className="flex-1">
              <Link href="/">
                <Home className="mr-2 h-4 w-4" />
                {t("backHome")}
              </Link>
            </Button>
            <Button asChild variant="outline" className="flex-1">
              <Link href="/exercises">
                <Search className="mr-2 h-4 w-4" />
                Voir les exercices
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
