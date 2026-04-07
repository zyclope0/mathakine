"use client";

import Link from "next/link";
import { Home, LogOut, User, Settings, ChevronDown, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export interface HeaderUserMenuProps {
  user: { username?: string; email?: string | null } | null | undefined;
  userMenuAriaLabel: string;
  onLogout: () => void;
  profileLabel: string;
  settingsLabel: string;
  dashboardLabel: string;
  adminLabel: string;
  logoutLabel: string;
  hasFullAccess: boolean;
  isStudent: boolean;
  isAdmin: boolean;
}

export function HeaderUserMenu({
  user,
  userMenuAriaLabel,
  onLogout,
  profileLabel,
  settingsLabel,
  dashboardLabel,
  adminLabel,
  logoutLabel,
  hasFullAccess,
  isStudent,
  isAdmin,
}: HeaderUserMenuProps) {
  return (
    <div className="flex items-center gap-2">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="flex items-center gap-2 h-9 px-3"
            aria-label={userMenuAriaLabel}
            aria-haspopup="menu"
          >
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
                <User className="h-4 w-4 text-primary" aria-hidden="true" />
              </div>
              <span className="hidden sm:inline text-sm font-medium">{user?.username}</span>
              <ChevronDown
                className="h-3 w-3 text-muted-foreground hidden sm:inline"
                aria-hidden="true"
              />
            </div>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel className="font-normal">
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium leading-none">{user?.username}</p>
              {user?.email ? (
                <p className="text-xs leading-none text-muted-foreground truncate">{user.email}</p>
              ) : null}
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link href="/profile" className="flex items-center cursor-pointer">
              <User className="mr-2 h-4 w-4" />
              <span>{profileLabel}</span>
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/settings" className="flex items-center cursor-pointer">
              <Settings className="mr-2 h-4 w-4" />
              <span>{settingsLabel}</span>
            </Link>
          </DropdownMenuItem>
          {hasFullAccess && isStudent ? (
            <DropdownMenuItem asChild>
              <Link href="/dashboard" className="flex items-center cursor-pointer">
                <Home className="mr-2 h-4 w-4" />
                <span>{dashboardLabel}</span>
              </Link>
            </DropdownMenuItem>
          ) : null}
          {isAdmin ? (
            <DropdownMenuItem asChild>
              <Link href="/admin" className="flex items-center cursor-pointer">
                <Shield className="mr-2 h-4 w-4" />
                <span>{adminLabel}</span>
              </Link>
            </DropdownMenuItem>
          ) : null}
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => onLogout()} variant="destructive">
            <LogOut className="mr-2 h-4 w-4" />
            <span>{logoutLabel}</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
