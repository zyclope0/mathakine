"use client";

import { useSearchParams } from "next/navigation";
import { useAdminContentPageController } from "@/hooks/useAdminContentPageController";
import { PageHeader, PageSection } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { AdminContentTabsNav } from "@/components/admin/content/AdminContentTabsNav";
import { AdminExercisesSection } from "@/components/admin/content/AdminExercisesSection";
import { AdminChallengesSection } from "@/components/admin/content/AdminChallengesSection";
import { AdminBadgesSection } from "@/components/admin/content/AdminBadgesSection";

export default function AdminContentPage() {
  const searchParams = useSearchParams();
  const { defaultTab, editId } = useAdminContentPageController(searchParams);

  return (
    <div className="space-y-8">
      <PageHeader title="Contenu" description="Exercices, défis logiques et badges — archivage" />

      <PageSection>
        <Card>
          <CardContent className="pt-6">
            <AdminContentTabsNav
              defaultTab={defaultTab}
              exercisesContent={
                <AdminExercisesSection
                  key={`exercises-${editId ?? ""}`}
                  initialEditId={defaultTab === "exercises" ? editId : null}
                />
              }
              challengesContent={
                <AdminChallengesSection
                  key={`challenges-${editId ?? ""}`}
                  initialEditId={defaultTab === "challenges" ? editId : null}
                />
              }
              badgesContent={
                <AdminBadgesSection
                  key={`badges-${editId ?? ""}`}
                  initialEditId={defaultTab === "badges" ? editId : null}
                />
              }
            />
          </CardContent>
        </Card>
      </PageSection>
    </div>
  );
}
