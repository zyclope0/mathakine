"use client";

/**
 * Mobile section Select + desktop sidebar for settings.
 * Pure presentation; section state owned by controller via props.
 * FFI-L13 lot B.
 */

import type { LucideIcon } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import type { SettingsSection } from "@/lib/settings/settingsPage";

export interface SettingsMenuItem {
  id: SettingsSection;
  label: string;
  icon: LucideIcon;
}

export interface SettingsSidebarNavProps {
  menuItems: SettingsMenuItem[];
  activeSection: SettingsSection;
  onSectionChange: (section: SettingsSection) => void;
}

export function SettingsSidebarNav({
  menuItems,
  activeSection,
  onSectionChange,
}: SettingsSidebarNavProps) {
  return (
    <>
      <div className="md:hidden">
        <Select value={activeSection} onValueChange={(v) => onSectionChange(v as SettingsSection)}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {menuItems.map((item) => (
              <SelectItem key={item.id} value={item.id}>
                <span className="flex items-center gap-2">
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <nav className="hidden md:flex md:col-span-3 flex-col gap-1">
        {menuItems.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onSectionChange(item.id)}
            className={cn(
              "flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors",
              activeSection === item.id
                ? "text-foreground bg-muted/80"
                : "text-muted-foreground hover:bg-muted/50"
            )}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {item.label}
          </button>
        ))}
      </nav>
    </>
  );
}
