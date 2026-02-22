"use client";

import { useState } from "react";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAdminAuditLog, getAuditActionLabel } from "@/hooks/useAdminAuditLog";
import { ChevronLeft, ChevronRight, FileText } from "lucide-react";

const PAGE_SIZE = 30;

const RESOURCE_TYPES = [
  { value: "all", label: "Tous types" },
  { value: "user", label: "Utilisateur" },
  { value: "exercise", label: "Exercice" },
  { value: "challenge", label: "Défi" },
];

const ACTIONS = [
  { value: "all", label: "Toutes actions" },
  { value: "user_patch", label: "Modif. utilisateur" },
  { value: "exercise_create", label: "Création exercice" },
  { value: "exercise_update", label: "Modif. exercice" },
  { value: "exercise_archive", label: "Archivage exercice" },
  { value: "exercise_duplicate", label: "Duplication exercice" },
  { value: "challenge_create", label: "Création défi" },
  { value: "challenge_update", label: "Modif. défi" },
  { value: "challenge_archive", label: "Archivage défi" },
  { value: "challenge_duplicate", label: "Duplication défi" },
  { value: "export_csv", label: "Export CSV" },
];

export default function AdminAuditLogPage() {
  const [page, setPage] = useState(0);
  const [actionFilter, setActionFilter] = useState<string>("all");
  const [resourceFilter, setResourceFilter] = useState<string>("all");

  const { items, total, isLoading, error } = useAdminAuditLog({
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    ...(actionFilter !== "all" && { action: actionFilter }),
    ...(resourceFilter !== "all" && { resource_type: resourceFilter }),
  });

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;

  return (
    <div className="space-y-8">
      <PageHeader
        title="Journal d'audit"
        description="Historique des actions effectuées par les administrateurs"
      />

      <PageSection>
        <Card>
          <CardContent className="pt-6">
            <div className="mb-4 flex flex-wrap gap-3 items-end">
              <Select
                value={actionFilter}
                onValueChange={(v) => {
                  setActionFilter(v);
                  setPage(0);
                }}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Action" />
                </SelectTrigger>
                <SelectContent>
                  {ACTIONS.map((a) => (
                    <SelectItem key={a.value} value={a.value}>
                      {a.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={resourceFilter}
                onValueChange={(v) => {
                  setResourceFilter(v);
                  setPage(0);
                }}
              >
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Ressource" />
                </SelectTrigger>
                <SelectContent>
                  {RESOURCE_TYPES.map((r) => (
                    <SelectItem key={r.value} value={r.value}>
                      {r.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {error ? (
              <p className="py-8 text-center text-destructive">
                Erreur de chargement. Vérifiez vos droits.
              </p>
            ) : isLoading ? (
              <LoadingState message="Chargement du journal..." />
            ) : items.length === 0 ? (
              <div className="py-12 text-center text-muted-foreground">
                <FileText className="mx-auto h-12 w-12 opacity-50 mb-2" />
                <p>Aucune action enregistrée.</p>
                <p className="text-sm mt-1">Les nouvelles actions admin seront affichées ici.</p>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto rounded-md border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">Date</th>
                        <th className="px-4 py-3 text-left font-medium">Admin</th>
                        <th className="px-4 py-3 text-left font-medium">Action</th>
                        <th className="px-4 py-3 text-left font-medium">Ressource</th>
                        <th className="px-4 py-3 text-left font-medium">Détails</th>
                      </tr>
                    </thead>
                    <tbody>
                      {items.map((log, idx) => (
                        <tr
                          key={log.id}
                          className={`border-b last:border-0 ${idx % 2 === 1 ? "bg-muted/30" : ""}`}
                        >
                          <td className="px-4 py-3 text-muted-foreground text-xs whitespace-nowrap">
                            {log.created_at
                              ? new Date(log.created_at).toLocaleString("fr-FR")
                              : "-"}
                          </td>
                          <td className="px-4 py-3">
                            {log.admin_username ??
                              (log.admin_user_id != null ? `#${log.admin_user_id}` : "-")}
                          </td>
                          <td className="px-4 py-3">{getAuditActionLabel(log.action)}</td>
                          <td className="px-4 py-3">
                            {log.resource_type}
                            {log.resource_id != null ? ` #${log.resource_id}` : ""}
                          </td>
                          <td className="px-4 py-3 text-muted-foreground text-xs max-w-[200px] truncate">
                            {log.details ? JSON.stringify(log.details) : "-"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {totalPages > 1 && (
                  <div className="mt-4 flex items-center justify-between">
                    <p className="text-sm text-muted-foreground">
                      {total} entrée(s) — Page {page + 1} / {totalPages}
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.max(0, p - 1))}
                        disabled={page === 0}
                      >
                        <ChevronLeft className="h-4 w-4" />
                        Précédent
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                        disabled={page >= totalPages - 1}
                      >
                        Suivant
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </PageSection>
    </div>
  );
}
