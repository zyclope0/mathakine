"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Toaster } from "@/components/ui/sonner";
import { NextIntlProvider } from "./NextIntlProvider";
import { AuthSyncProvider } from "./AuthSyncProvider";
import { AccessScopeSync } from "./AccessScopeSync";
import { ThemeBootstrap } from "./ThemeBootstrap";
import { AccessibilityDomSync } from "./AccessibilityDomSync";
import { AccessibilityHotkeys } from "./AccessibilityHotkeys";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeBootstrap />
        <AccessibilityDomSync />
        <AccessibilityHotkeys />
        <AuthSyncProvider>
          <AccessScopeSync />
          {children}
        </AuthSyncProvider>
        <Toaster />
        {process.env.NODE_ENV === "development" && (
          <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-left" />
        )}
      </QueryClientProvider>
    </NextIntlProvider>
  );
}
