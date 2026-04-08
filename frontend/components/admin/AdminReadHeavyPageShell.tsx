"use client";

import type { ReactNode } from "react";
import { PageHeader, PageSection } from "@/components/layout";
import { AdminStatePanel } from "@/components/admin/AdminStatePanel";

export interface AdminReadHeavyPageShellProps {
  title: string;
  description: string;
  /** Filters / actions row above the state panel (period selectors, etc.). */
  toolbar?: ReactNode;
  hasError: boolean;
  errorMessage: string;
  isLoading: boolean;
  loadingMessage: string;
  /** When true, shows the global empty card (analytics-style) instead of children. */
  isEmpty?: boolean;
  emptyMessage?: string;
  children: ReactNode;
}

/**
 * Outer shell for admin routes that share: space-y-8, PageHeader, PageSection, toolbar strip, AdminStatePanel.
 * FFI-L20F — `/admin` overview keeps PageLayout in page.tsx; analytics + ai-monitoring use this shell.
 */
export function AdminReadHeavyPageShell({
  title,
  description,
  toolbar,
  hasError,
  errorMessage,
  isLoading,
  loadingMessage,
  isEmpty,
  emptyMessage,
  children,
}: AdminReadHeavyPageShellProps) {
  return (
    <div className="space-y-8">
      <PageHeader title={title} description={description} />
      <PageSection>
        {toolbar ? <div className="mb-4 flex flex-wrap items-center gap-4">{toolbar}</div> : null}
        <AdminStatePanel
          hasError={hasError}
          errorMessage={errorMessage}
          isLoading={isLoading}
          loadingMessage={loadingMessage}
          isEmpty={isEmpty === true}
          {...(emptyMessage !== undefined ? { emptyMessage } : {})}
        >
          {children}
        </AdminStatePanel>
      </PageSection>
    </div>
  );
}
