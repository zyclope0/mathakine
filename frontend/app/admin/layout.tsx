"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/hooks/useAuth";
import { PageLayout } from "@/components/layout";
import { cn } from "@/lib/utils";
import { BookOpen, Bot, FileText, LayoutDashboard, Settings, Users } from "lucide-react";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const isAdmin = user?.role === "archiviste";

  useEffect(() => {
    if (!isLoading && user && !isAdmin) {
      router.push("/dashboard");
    }
  }, [isLoading, user, isAdmin, router]);

  if (!user && !isLoading) return null;
  if (!isAdmin && user) return null;

  const navItems = [
    { href: "/admin", label: "Vue d'ensemble", icon: LayoutDashboard },
    { href: "/admin/users", label: "Utilisateurs", icon: Users },
    { href: "/admin/content", label: "Contenu", icon: BookOpen },
    { href: "/admin/moderation", label: "Modération IA", icon: Bot },
    { href: "/admin/audit-log", label: "Journal d'audit", icon: FileText },
    { href: "/admin/config", label: "Paramètres", icon: Settings },
  ];

  return (
    <ProtectedRoute>
      <PageLayout maxWidth="2xl">
        <div className="flex flex-col gap-6 md:flex-row">
          <nav className="flex shrink-0 flex-col gap-1 md:w-48">
            {navItems.map(({ href, label, icon: Icon }) => {
              const isActive = href === "/admin" ? pathname === "/admin" : pathname.startsWith(href);
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
