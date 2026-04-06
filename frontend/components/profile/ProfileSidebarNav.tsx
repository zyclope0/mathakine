"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { User, Palette, BarChart3 } from "lucide-react";
import type { ProfileSection } from "@/lib/profile/profilePage";

interface NavItem {
  id: ProfileSection;
  label: string;
  icon: typeof User;
}

interface ProfileSidebarNavProps {
  activeSection: ProfileSection;
  onSectionChange: (section: ProfileSection) => void;
  items: NavItem[];
}

/**
 * Navigation de la page profil — sidebar desktop + select mobile.
 * Composant purement visuel + callbacks.
 *
 * FFI-L11.
 */
export function ProfileSidebarNav({
  activeSection,
  onSectionChange,
  items,
}: ProfileSidebarNavProps) {
  return (
    <>
      {/* Mobile: Select */}
      <div className="md:hidden">
        <Select value={activeSection} onValueChange={(v) => onSectionChange(v as ProfileSection)}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {items.map((item) => (
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

      {/* Sidebar (desktop) */}
      <nav className="hidden md:flex md:col-span-3 flex-col gap-1">
        {items.map((item) => (
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

// Export de l'icône par défaut pour que page.tsx puisse construire menuItems
export { User, Palette, BarChart3 };
export type { NavItem };
