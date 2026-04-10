"use client";

import { useCallback, useState } from "react";
import {
  CONTENT_LIST_ORDER,
  type ContentListOrder,
  isValidStoredContentListOrder,
} from "@/lib/constants/contentListOrder";
import { getLocalString, removeLocalKey, setLocalString, type STORAGE_KEYS } from "@/lib/storage";

type OrderPreferenceStorageKey =
  | typeof STORAGE_KEYS.prefExerciseOrder
  | typeof STORAGE_KEYS.prefChallengeOrder;

function readStoredOrder(storageKey: OrderPreferenceStorageKey): ContentListOrder {
  if (typeof window === "undefined") return CONTENT_LIST_ORDER.RANDOM;
  const raw = getLocalString(storageKey);
  return isValidStoredContentListOrder(raw) ? raw : CONTENT_LIST_ORDER.RANDOM;
}

/**
 * Hydrates list sort preference from localStorage on mount; persists on change.
 * `orderPreferenceStorageKey` is stable for each hook instance (separate routes use separate mounts).
 */
export function useContentListOrderPreference(storageKey: OrderPreferenceStorageKey) {
  const [orderFilter, setOrderFilter] = useState<ContentListOrder>(() =>
    readStoredOrder(storageKey)
  );

  const handleOrderChange = useCallback(
    (value: ContentListOrder) => {
      setOrderFilter(value);
      setLocalString(storageKey, value);
    },
    [storageKey]
  );

  const resetOrderPreference = useCallback(() => {
    setOrderFilter(CONTENT_LIST_ORDER.RANDOM);
    removeLocalKey(storageKey);
  }, [storageKey]);

  return { orderFilter, handleOrderChange, resetOrderPreference };
}
