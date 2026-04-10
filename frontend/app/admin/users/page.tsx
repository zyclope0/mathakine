"use client";

import { useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import type { AdminUser } from "@/hooks/useAdminUsers";
import type { UserRole } from "@/lib/auth/userRoles";
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
  Trash2,
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
import { normalizeUserRole } from "@/lib/auth/userRoles";

const ROLE_VALUES = ["all", "apprenant", "enseignant", "moderateur", "admin"] as const;

const PAGE_SIZE = 20;

function localeTag(locale: string): string {
  return locale === "en" ? "en-US" : "fr-FR";
}

export default function AdminUsersPage() {
  const t = useTranslations("adminPages.users");
  const tToast = useTranslations("adminPages.users.toast");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const dateLocale = localeTag(locale);

  const [search, setSearch] = useState("");
  const [role, setRole] = useState<UserRole | "all">("all");
  const [isActiveFilter, setIsActiveFilter] = useState<string>("all");
  const [page, setPage] = useState(0);
  const [roleEditUser, setRoleEditUser] = useState<AdminUser | null>(null);
  const [roleEditValue, setRoleEditValue] = useState<UserRole>("apprenant");
  const [deleteConfirmUser, setDeleteConfirmUser] = useState<AdminUser | null>(null);

  const isActive = isActiveFilter === "all" ? undefined : isActiveFilter === "true";

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
    deleteUser,
    isUpdating,
    isSendingReset,
    isResendingVerification,
    isDeleting,
  } = useAdminUsers({
    ...(search && { search }),
    ...(role !== "all" && { role }),
    ...(isActive !== undefined && { is_active: isActive }),
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
  });

  const roles = useMemo(
    () =>
      ROLE_VALUES.map((value) => ({
        value,
        label: t(`roles.${value}`),
      })),
    [t]
  );

  const roleLabel = (roleValue: string) => {
    const n = normalizeUserRole(roleValue);
    if (!n) return roleValue;
    return t(`roles.${n}`);
  };

  const handleToggleActive = async (u: { id: number; username: string; is_active: boolean }) => {
    try {
      await updateUserActive({ userId: u.id, isActive: !u.is_active });
      toast.success(u.is_active ? tToast("deactivated") : tToast("reactivated"), {
        description: u.is_active
          ? tToast("deactivatedDesc", { username: u.username })
          : tToast("reactivatedDesc", { username: u.username }),
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : tToast("updateFailed");
      toast.error(tToast("errorTitle"), { description: msg });
    }
  };

  const handleUpdateRole = async (u: AdminUser, newRole: UserRole) => {
    try {
      await updateUserRole({ userId: u.id, role: newRole });
      toast.success(tToast("roleChanged"), {
        description: tToast("roleChangedDesc", {
          username: u.username,
          role: roleLabel(newRole),
        }),
      });
      setRoleEditUser(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : tToast("updateFailed");
      toast.error(tToast("errorTitle"), { description: msg });
    }
  };

  const handleSendResetPassword = async (u: AdminUser) => {
    try {
      await sendResetPassword(u.id);
      toast.success(tToast("emailSent"), {
        description: tToast("resetDesc", { email: u.email }),
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : tToast("sendFailed");
      toast.error(tToast("errorTitle"), { description: msg });
    }
  };

  const handleResendVerification = async (u: AdminUser) => {
    try {
      await resendVerification(u.id);
      toast.success(tToast("emailSent"), {
        description: tToast("verifyDesc", { email: u.email }),
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : tToast("sendFailed");
      toast.error(tToast("errorTitle"), { description: msg });
    }
  };

  const handleDeleteUser = async (u: AdminUser) => {
    try {
      await deleteUser(u.id);
      toast.success(tToast("userDeleted"), {
        description: tToast("userDeletedDesc", { username: u.username }),
      });
      setDeleteConfirmUser(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : tToast("deleteFailed");
      toast.error(tToast("errorTitle"), { description: msg });
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;
  const hasNext = page < totalPages - 1;
  const hasPrev = page > 0;

  return (
    <div className="space-y-8">
      <PageHeader title={t("title")} description={t("description")} />

      <PageSection>
        <Card>
          <CardContent className="pt-6">
            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end">
              <div className="flex-1">
                <Label htmlFor="admin-users-search" className="sr-only">
                  {t("searchLabel")}
                </Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="admin-users-search"
                    placeholder={t("searchPlaceholder")}
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
                    setRole(v as UserRole | "all");
                    setPage(0);
                  }}
                >
                  <SelectTrigger className="w-[160px]">
                    <SelectValue placeholder={t("rolePlaceholder")} />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map((r) => (
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
                    <SelectValue placeholder={t("statusPlaceholder")} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">{t("statusAll")}</SelectItem>
                    <SelectItem value="true">{t("statusActive")}</SelectItem>
                    <SelectItem value="false">{t("statusInactive")}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {error ? (
              <p className="text-center py-8 text-destructive">{t("errorLoading")}</p>
            ) : isLoading ? (
              <LoadingState message={t("loading")} />
            ) : (
              <>
                <div className="overflow-x-auto rounded-md border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">{t("colUser")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colEmail")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colRole")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colStatus")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colSignup")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colActions")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="px-4 py-12 text-center text-muted-foreground">
                            {t("empty")}
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
                              <Badge variant="secondary">{roleLabel(u.role)}</Badge>
                            </td>
                            <td className="px-4 py-3">
                              <Badge variant={u.is_active ? "default" : "outline"}>
                                {u.is_active ? t("statusActive") : t("statusInactive")}
                              </Badge>
                            </td>
                            <td className="px-4 py-3 text-muted-foreground text-xs">
                              {u.created_at
                                ? new Date(u.created_at).toLocaleDateString(dateLocale)
                                : "-"}
                            </td>
                            <td className="px-4 py-3">
                              {currentUser?.id !== u.id ? (
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      disabled={isUpdating || isDeleting}
                                    >
                                      <MoreHorizontal className="h-4 w-4" />
                                      <span className="sr-only">{t("actionsMenu")}</span>
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end">
                                    <DropdownMenuItem
                                      onClick={() => {
                                        setRoleEditUser(u);
                                        setRoleEditValue(normalizeUserRole(u.role) ?? "apprenant");
                                      }}
                                    >
                                      <Shield className="h-4 w-4" />
                                      {t("menuChangeRole")}
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                      onClick={() => handleSendResetPassword(u)}
                                      disabled={isSendingReset}
                                    >
                                      <Mail className="h-4 w-4" />
                                      {t("menuSendReset")}
                                    </DropdownMenuItem>
                                    {u.is_email_verified === false && (
                                      <DropdownMenuItem
                                        onClick={() => handleResendVerification(u)}
                                        disabled={isResendingVerification}
                                      >
                                        <MailCheck className="h-4 w-4" />
                                        {t("menuResendVerify")}
                                      </DropdownMenuItem>
                                    )}
                                    <DropdownMenuItem
                                      onClick={() => handleToggleActive(u)}
                                      variant={u.is_active ? "destructive" : "default"}
                                    >
                                      {u.is_active ? (
                                        <>
                                          <UserX className="h-4 w-4" /> {t("menuDeactivate")}
                                        </>
                                      ) : (
                                        <>
                                          <UserCheck className="h-4 w-4" /> {t("menuActivate")}
                                        </>
                                      )}
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                      onClick={() => setDeleteConfirmUser(u)}
                                      className="text-destructive focus:text-destructive"
                                      disabled={isDeleting}
                                    >
                                      <Trash2 className="h-4 w-4" /> {t("menuDelete")}
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              ) : (
                                <span className="text-xs text-muted-foreground">{t("you")}</span>
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
                      {t("pagination", {
                        total,
                        current: page + 1,
                        pages: totalPages,
                      })}
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.max(0, p - 1))}
                        disabled={!hasPrev}
                      >
                        <ChevronLeft className="h-4 w-4" />
                        {tCommon("previous")}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                        disabled={!hasNext}
                      >
                        {tCommon("next")}
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
              <DialogTitle>{t("dialogRoleTitle")}</DialogTitle>
              <p className="text-sm text-muted-foreground">
                {roleEditUser ? `${roleEditUser.username} (${roleEditUser.email})` : ""}
              </p>
            </DialogHeader>
            {roleEditUser && (
              <div className="flex flex-col gap-4 py-4">
                <div>
                  <Label className="mb-2 block">{t("newRoleLabel")}</Label>
                  {roleEditUser && (
                    <p className="mb-2 text-xs text-muted-foreground">
                      {t("currentRole", { role: roleLabel(roleEditUser.role) })}
                    </p>
                  )}
                  <Select
                    value={roleEditValue}
                    onValueChange={(v) => setRoleEditValue(v as UserRole)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t("chooseRolePlaceholder")} />
                    </SelectTrigger>
                    <SelectContent>
                      {roles
                        .filter((r) => r.value !== "all")
                        .map((r) => (
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
                {t("cancel")}
              </Button>
              <Button
                onClick={() => roleEditUser && handleUpdateRole(roleEditUser, roleEditValue)}
                disabled={!roleEditUser || roleEditValue === roleEditUser.role}
              >
                {t("save")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog
          open={!!deleteConfirmUser}
          onOpenChange={(open) => {
            if (!open) setDeleteConfirmUser(null);
          }}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t("deleteTitle")}</DialogTitle>
              <p className="text-sm text-muted-foreground">
                {deleteConfirmUser
                  ? t("deleteBody", {
                      username: deleteConfirmUser.username,
                      email: deleteConfirmUser.email,
                    })
                  : ""}
              </p>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDeleteConfirmUser(null)}>
                {t("cancel")}
              </Button>
              <Button
                variant="destructive"
                onClick={() => deleteConfirmUser && handleDeleteUser(deleteConfirmUser)}
                disabled={!deleteConfirmUser || isDeleting}
              >
                {isDeleting ? t("deleteWorking") : t("deleteConfirm")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </PageSection>
    </div>
  );
}
