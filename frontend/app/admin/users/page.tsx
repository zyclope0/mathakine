"use client";

import { useTranslations } from "next-intl";
import type { UserRole } from "@/lib/auth/userRoles";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAdminUsersPageController } from "@/hooks/useAdminUsersPageController";
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

export default function AdminUsersPage() {
  const tCommon = useTranslations("common");
  const {
    t,
    dateLocale,
    roles,
    roleLabel,
    search,
    setSearchQuery,
    role,
    setRoleFilter,
    isActiveFilter,
    setStatusFilter,
    page,
    setPage,
    roleEditUser,
    roleEditValue,
    setRoleEditValue,
    deleteConfirmUser,
    setDeleteConfirmUser,
    openRoleEditor,
    closeRoleDialog,
    closeDeleteDialog,
    users,
    total,
    isLoading,
    error,
    currentUser,
    isUpdating,
    isSendingReset,
    isResendingVerification,
    isDeleting,
    handleToggleActive,
    handleUpdateRole,
    handleSendResetPassword,
    handleResendVerification,
    handleDeleteUser,
    totalPages,
    hasNext,
    hasPrev,
  } = useAdminUsersPageController();

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
                      setSearchQuery(e.target.value);
                    }}
                    className="pl-9"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Select
                  value={role}
                  onValueChange={(v) => {
                    setRoleFilter(v as UserRole | "all");
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
                    setStatusFilter(v);
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
                                    <DropdownMenuItem onClick={() => openRoleEditor(u)}>
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
            if (!open) closeRoleDialog();
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
              <Button variant="outline" onClick={closeRoleDialog}>
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
            if (!open) closeDeleteDialog();
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
              <Button variant="outline" onClick={closeDeleteDialog}>
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
