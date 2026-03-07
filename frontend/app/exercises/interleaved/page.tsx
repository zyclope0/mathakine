"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout } from "@/components/layout";
import { Loader2 } from "lucide-react";
import { api, ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { useTranslations } from "next-intl";

const INTERLEAVED_STORAGE_KEY = "interleaved_session";

export interface InterleavedPlan {
  session_kind: string;
  length: number;
  eligible_types: string[];
  plan: string[];
  message_key: string;
}

export default function InterleavedPage() {
  const router = useRouter();
  const t = useTranslations("dashboard.quickStart");
  const tSolver = useTranslations("exercises.solver");
  const [status, setStatus] = useState<"loading" | "error">("loading");

  useEffect(() => {
    let cancelled = false;

    async function run() {
      try {
        const plan = await api.get<InterleavedPlan>(
          "/api/exercises/interleaved-plan?length=10"
        );

        if (cancelled) return;

        if (!plan.plan || plan.plan.length === 0) {
          toast.info(t("interleavedNotEnoughVariety"));
          router.replace("/exercises");
          return;
        }

        const firstType = plan.plan[0];
        const exercise = await api.post<{ id: number }>("/api/exercises/generate", {
          exercise_type: firstType,
          adaptive: true,
          save: true,
        });

        if (cancelled) return;

        if (exercise?.id) {
          sessionStorage.setItem(
            INTERLEAVED_STORAGE_KEY,
            JSON.stringify({
              plan: plan.plan,
              completedCount: 0,
              length: plan.length,
            })
          );
          router.replace(`/exercises/${exercise.id}?session=interleaved`);
        } else {
          setStatus("error");
        }
      } catch (err) {
        if (cancelled) return;

        if (err instanceof ApiClientError && err.status === 409) {
          const detail = err.details as { detail?: { code?: string } } | undefined;
          if (detail?.detail?.code === "not_enough_variety") {
            toast.info(t("interleavedNotEnoughVariety"));
            router.replace("/exercises");
            return;
          }
        }

        toast.error(err instanceof Error ? err.message : "Erreur");
        setStatus("error");
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [router, t]);

  return (
    <ProtectedRoute>
      <PageLayout>
        <div className="flex flex-col items-center justify-center min-h-[300px] gap-4">
          {status === "loading" && (
            <>
              <Loader2 className="h-10 w-10 animate-spin text-primary" />
              <div className="space-y-2 text-center">
                <p className="font-medium text-foreground">{t("interleavedCta")}</p>
                <p className="text-muted-foreground">{t("interleavedPedagogy")}</p>
              </div>
            </>
          )}
          {status === "error" && (
            <button
              type="button"
              onClick={() => router.replace("/exercises")}
              className="text-primary hover:underline"
            >
              {tSolver("backToExercises")}
            </button>
          )}
        </div>
      </PageLayout>
    </ProtectedRoute>
  );
}
