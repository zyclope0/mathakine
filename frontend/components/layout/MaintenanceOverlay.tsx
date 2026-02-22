"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export function MaintenanceOverlay() {
  const [show, setShow] = useState(false);
  const pathname = usePathname();
  const { user } = useAuth();
  const isAdmin = user?.role === "archiviste";

  // Ne pas bloquer l'accès au login et à l'admin : permet à l'archiviste de se reconnecter en maintenance
  const isAuthOrAdminRoute = pathname === "/login" || pathname?.startsWith("/admin");

  useEffect(() => {
    const onMaintenance = () => setShow(true);
    window.addEventListener("maintenance", onMaintenance);
    return () => window.removeEventListener("maintenance", onMaintenance);
  }, []);

  if (!show || isAdmin || isAuthOrAdminRoute) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-background/95 backdrop-blur-sm"
      role="alert"
      aria-live="assertive"
    >
      <div className="mx-4 max-w-md rounded-xl border bg-card p-8 text-center shadow-lg">
        <h2 className="text-xl font-semibold text-foreground">Le temple est en maintenance</h2>
        <p className="mt-3 text-muted-foreground">Réessayez dans quelques instants.</p>
        <div className="mt-6 flex flex-col gap-2 sm:flex-row sm:justify-center">
          <a
            href="/login"
            className="rounded-lg border bg-background px-4 py-2 text-sm font-medium text-foreground hover:bg-muted"
          >
            Accès admin
          </a>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            Actualiser
          </button>
        </div>
      </div>
    </div>
  );
}
