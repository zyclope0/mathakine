"use client";

import { useState } from "react";
import type { AdminUser } from "@/hooks/useAdminUsers";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { useAdminUsers } from "@/hooks/useAdminUsers";
import { useAuth } from "@/hooks/useAuth";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Search,
  ChevronLeft,
  ChevronRight,
  UserX,
  UserCheck,
  MoreHorizontal,
  Shield,
  Mail,
  MailCheck,
} from "lucide-react";
import { Label } from "@/components/ui/label";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const ROLES = [
  { value: "all", label: "Tous les rôles" },
  { value: "padawan", label: "Padawan" },
  { value: "maitre", label: "Maître" },
  { value: "gardien", label: "Gardien" },
  { value: "archiviste", label: "Archiviste" },
];

const ROLE_LABELS: Record<string, string> = {
  padawan: "Padawan",
  maitre: "Maître",
  gardien: "Gardien",
  archiviste: "Archiviste",
};

const PAGE_SIZE = 20;

export default function AdminUsersPage() {
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("all");
  const [isActiveFilter, setIsActiveFilter] = useState<string>("all");
  const [page, setPage] = useState(0);
  const [roleEditUser, setRoleEditUser] = useState<AdminUser | null>(null);
  const [roleEditValue, setRoleEditValue] = useState<string>("");

  const isActive =
    isActiveFilter === "all"
      ? undefined
      : isActiveFilter === "true";

  const { user: currentUser } = useAuth();
  const {
    users,
    total,
    isLoading,
    error,
    updateUserActive,
    updateUserRole,
    sendResetPassword,
    resendVerification,
    isUpdating,
    isSendingReset,
    isResendingVerification,
  } = useAdminUsers({
    ...(search && { search }),
    ...(role !== "all" && { role }),
    ...(isActive !== undefined && { is_active: isActive }),
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
  });

  const handleToggleActive = async (u: { id: number; username: string; is_active: boolean }) => {
    try {
      await updateUserActive({ userId: u.id, isActive: !u.is_active });
      toast.success(u.is_active ? "Compte désactivé" : "Compte réactivé", {
        description: `${u.username} a été ${u.is_active ? "désactivé" : "réactivé"}.`,
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erreur lors de la mise à jour";
      toast.error("Erreur", { description: msg });
    }
  };

  const handleUpdateRole = async (u: AdminUser, newRole: string) => {
    try {
      await updateUserRole({ userId: u.id, role: newRole });
      toast.success("Rôle modifié", { description: `${u.username} → ${ROLE_LABELS[newRole] ?? newRole}` });
      setRoleEditUser(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erreur lors de la mise à jour";
      toast.error("Erreur", { description: msg });
    }
  };

  const handleSendResetPassword = async (u: AdminUser) => {
    try {
      await sendResetPassword(u.id);
      toast.success("Email envoyé", { description: `Lien de réinitialisation envoyé à ${u.email}` });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Échec de l'envoi";
      toast.error("Erreur", { description: msg });
    }
  };

  const handleResendVerification = async (u: AdminUser) => {
    try {
      await resendVerification(u.id);
      toast.success("Email envoyé", { description: `Email de vérification envoyé à ${u.email}` });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Échec de l'envoi";
      toast.error("Erreur", { description: msg });
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;
  const hasNext = page < totalPages - 1;
  const hasPrev = page > 0;

  return (
    <>
      <PageHeader
        title="Utilisateurs"
        description="Liste des utilisateurs de la plateforme"
      />

      <PageSection>
        <Card>
          <CardContent className="pt-6">
            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end">
              <div className="flex-1">
                <Label htmlFor="admin-users-search" className="sr-only">
                  Rechercher
                </Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="admin-users-search"
                    placeholder="Rechercher (pseudo, email, nom)"
                    value={search}
                    onChange={(e) => {
                      setSearch(e.target.value);
                      setPage(0);
                    }}
                    className="pl-9"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Select
                  value={role}
                  onValueChange={(v) => {
                    setRole(v);
                    setPage(0);
                  }}
                >
                  <SelectTrigger className="w-[160px]">
                    <SelectValue placeholder="Rôle" />
                  </SelectTrigger>
                  <SelectContent>
                    {ROLES.map((r) => (
                      <SelectItem key={r.value} value={r.value}>
                        {r.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select
                  value={isActiveFilter}
                  onValueChange={(v) => {
                    setIsActiveFilter(v);
                    setPage(0);
                  }}
                >
                  <SelectTrigger className="w-[140px]">
                    <SelectValue placeholder="Statut" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tous</SelectItem>
                    <SelectItem value="true">Actifs</SelectItem>
                    <SelectItem value="false">Inactifs</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {error ? (
              <p className="text-center py-8 text-destructive">
                Erreur de chargement. Vérifiez vos droits.
              </p>
            ) : isLoading ? (
              <LoadingState message="Chargement des utilisateurs..." />
            ) : (
              <>
                <div className="overflow-x-auto rounded-md border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">Utilisateur</th>
                        <th className="px-4 py-3 text-left font-medium">Email</th>
                        <th className="px-4 py-3 text-left font-medium">Rôle</th>
                        <th className="px-4 py-3 text-left font-medium">Statut</th>
                        <th className="px-4 py-3 text-left font-medium">Inscription</th>
                        <th className="px-4 py-3 text-left font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="px-4 py-12 text-center text-muted-foreground">
                            Aucun utilisateur trouvé
                          </td>
                        </tr>
                      ) : (
                        users.map((u) => (
                          <tr key={u.id} className="border-b last:border-0">
                            <td className="px-4 py-3">
                              <span className="font-medium">{u.username}</span>
                              {u.full_name && (
                                <span className="block text-muted-foreground text-xs">
                                  {u.full_name}
                                </span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-muted-foreground">{u.email}</td>
                            <td className="px-4 py-3">
                              <Badge variant="secondary">
                                {ROLE_LABELS[u.role?.toLowerCase() ?? ""] ?? u.role}
                              </Badge>
                            </td>
                            <td className="px-4 py-3">
                              <Badge variant={u.is_active ? "default" : "outline"}>
                                {u.is_active ? "Actif" : "Inactif"}
                              </Badge>
                            </td>
                            <td className="px-4 py-3 text-muted-foreground text-xs">
                              {u.created_at
                                ? new Date(u.created_at).toLocaleDateString("fr-FR")
                                : "-"}
                            </td>
                            <td className="px-4 py-3">
                              {currentUser?.id !== u.id ? (
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="outline" size="sm" disabled={isUpdating}>
                                      <MoreHorizontal className="h-4 w-4" />
                                      <span className="sr-only">Actions</span>
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end">
                                    <DropdownMenuItem
                                      onClick={() => {
                                        setRoleEditUser(u);
                                        setRoleEditValue(u.role?.toLowerCase() ?? "padawan");
                                      }}
                                    >
                                      <Shield className="h-4 w-4" />
                                      Modifier le rôle
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                      onClick={() => handleSendResetPassword(u)}
                                      disabled={isSendingReset}
                                    >
                                      <Mail className="h-4 w-4" />
                                      Envoyer reset MDP
                                    </DropdownMenuItem>
                                    {u.is_email_verified === false && (
                                      <DropdownMenuItem
                                        onClick={() => handleResendVerification(u)}
                                        disabled={isResendingVerification}
                                      >
                                        <MailCheck className="h-4 w-4" />
                                        Renvoyer vérification
                                      </DropdownMenuItem>
                                    )}
                                    <DropdownMenuItem
                                      onClick={() => handleToggleActive(u)}
                                      variant={u.is_active ? "destructive" : "default"}
                                    >
                                      {u.is_active ? (
                                        <><UserX className="h-4 w-4" /> Désactiver</>
                                      ) : (
                                        <><UserCheck className="h-4 w-4" /> Activer</>
                                      )}
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              ) : (
                                <span className="text-xs text-muted-foreground">Vous</span>
                                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {totalPages > 1 && (
                  <div className="mt-4 flex items-center justify-between">
                    <p className="text-sm text-muted-foreground">
                      {total} utilisateur{total > 1 ? "s" : ""} — Page {page + 1} / {totalPages}
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.max(0, p - 1))}
                        disabled={!hasPrev}
                      >
                        <ChevronLeft className="h-4 w-4" />
                        Précédent
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                        disabled={!hasNext}
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

        <Dialog
          open={!!roleEditUser}
          onOpenChange={(open) => {
            if (!open) setRoleEditUser(null);
          }}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Modifier le rôle</DialogTitle>
              <p className="text-sm text-muted-foreground">
                {roleEditUser ? `${roleEditUser.username} (${roleEditUser.email})` : ""}
              </p>
            </DialogHeader>
            {roleEditUser && (
              <div className="flex flex-col gap-4 py-4">
                <div>
                  <Label className="mb-2 block">Nouveau rôle</Label>
                  <Select
                    value={roleEditValue}
                    onValueChange={setRoleEditValue}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ROLES.filter((r) => r.value !== "all").map((r) => (
                        <SelectItem key={r.value} value={r.value}>
                          {r.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setRoleEditUser(null)}>
                Annuler
              </Button>
              <Button
                onClick={() => roleEditUser && handleUpdateRole(roleEditUser, roleEditValue)}
                disabled={!roleEditUser || roleEditValue === (roleEditUser?.role?.toLowerCase() ?? "padawan")}
              >
                Enregistrer
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </PageSection>
    </>
  );
}
