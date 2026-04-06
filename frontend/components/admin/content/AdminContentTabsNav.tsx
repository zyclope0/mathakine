"use client";

import type { ReactNode } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { AdminContentTab } from "@/lib/admin/content/adminContentPage";

export interface AdminContentTabsNavProps {
  defaultTab: AdminContentTab;
  exercisesContent: ReactNode;
  challengesContent: ReactNode;
  badgesContent: ReactNode;
}

/**
 * Shell tabs only — no data fetching (FFI-L14 lot B).
 */
export function AdminContentTabsNav({
  defaultTab,
  exercisesContent,
  challengesContent,
  badgesContent,
}: AdminContentTabsNavProps) {
  return (
    <Tabs defaultValue={defaultTab} key={defaultTab}>
      <TabsList className="w-full flex flex-wrap gap-1 sm:gap-2 h-auto p-1">
        <TabsTrigger
          value="exercises"
          className="flex-1 min-w-[100px] sm:flex-initial sm:min-w-0 px-4"
        >
          Exercices
        </TabsTrigger>
        <TabsTrigger
          value="challenges"
          className="flex-1 min-w-[100px] sm:flex-initial sm:min-w-0 px-4"
        >
          Défis logiques
        </TabsTrigger>
        <TabsTrigger value="badges" className="flex-1 min-w-[80px] sm:flex-initial sm:min-w-0 px-4">
          Badges
        </TabsTrigger>
      </TabsList>
      <TabsContent value="exercises" className="mt-6">
        {exercisesContent}
      </TabsContent>
      <TabsContent value="challenges" className="mt-6">
        {challengesContent}
      </TabsContent>
      <TabsContent value="badges" className="mt-6">
        {badgesContent}
      </TabsContent>
    </Tabs>
  );
}
