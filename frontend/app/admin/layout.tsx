"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  BarChart3,
  BookOpen,
  Bot,
  FileText,
  LayoutDashboard,
  MessageCircle,
  Settings,
  Users,
} from "lucide-react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout } from "@/components/layout";
import { ADMIN_ROUTE_ACCESS } from "@/lib/auth/routeAccess";
import { cn } from "@/lib/utils";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const t = useTranslations("adminPages.layout");

  const navItems = [
    { href: "/admin", label: t("links.overview"), icon: LayoutDashboard },
    { href: "/admin/users", label: t("links.users"), icon: Users },
    { href: "/admin/analytics", label: t("links.analytics"), icon: BarChart3 },
    { href: "/admin/ai-monitoring", label: t("links.aiMonitoring"), icon: Bot },
    { href: "/admin/content", label: t("links.content"), icon: BookOpen },
    { href: "/admin/moderation", label: t("links.moderation"), icon: Bot },
    { href: "/admin/feedback", label: t("links.feedback"), icon: MessageCircle },
    { href: "/admin/audit-log", label: t("links.auditLog"), icon: FileText },
    { href: "/admin/config", label: t("links.config"), icon: Settings },
  ];

  return (
    <ProtectedRoute allowedRoles={ADMIN_ROUTE_ACCESS.allowedRoles}>
      <PageLayout maxWidth="2xl">
        <div className="flex flex-col gap-6 md:flex-row">
          <nav className="flex shrink-0 flex-col gap-1 md:w-48" aria-label={t("navAriaLabel")}>
            {navItems.map(({ href, label, icon: Icon }) => {
              const isActive =
                href === "/admin" ? pathname === "/admin" : pathname.startsWith(href);

              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </Link>
              );
            })}
          </nav>
          <main className="min-w-0 flex-1">{children}</main>
        </div>
      </PageLayout>
    </ProtectedRoute>
  );
}
