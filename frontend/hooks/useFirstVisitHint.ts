"use client";

import { useState } from "react";
import { getLocalString, setLocalString } from "@/lib/storage/browser-storage";

/**
 * Returns whether a first-visit hint should be shown, and a dismiss callback.
 *
 * Visible = true until the user explicitly dismisses (writes "1" to localStorage).
 * Safe on SSR: lazy useState initializer guards against missing `window`.
 *
 * @param storageKey - key from STORAGE_KEYS (lib/storage/keys.ts)
 */
export function useFirstVisitHint(storageKey: string): {
  visible: boolean;
  dismiss: () => void;
} {
  const [visible, setVisible] = useState<boolean>(() => {
    // Lazy initializer: runs once at mount. Returns false on SSR (no window).
    return getLocalString(storageKey) !== "1";
  });

  const dismiss = () => {
    setLocalString(storageKey, "1");
    setVisible(false);
  };

  return { visible, dismiss };
}
