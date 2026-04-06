"use client";

import { useMemo } from "react";
import {
  parseAdminContentEditIdParam,
  parseAdminContentTabParam,
  type AdminContentTab,
} from "@/lib/admin/content/adminContentPage";

export interface AdminContentPageShellState {
  defaultTab: AdminContentTab;
  editId: number | null;
}

/**
 * Shell-only state for `/admin/content` (tab + deep-link edit id from query).
 * Does not fetch data — domain hooks stay in tab components (FFI-L14 lot A).
 */
export function useAdminContentPageController(searchParams: {
  get: (key: string) => string | null;
}): AdminContentPageShellState {
  const tabParam = searchParams.get("tab");
  const editParam = searchParams.get("edit");

  return useMemo(
    () => ({
      defaultTab: parseAdminContentTabParam(tabParam),
      editId: parseAdminContentEditIdParam(editParam),
    }),
    [tabParam, editParam]
  );
}
