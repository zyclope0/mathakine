"use client";

import { useCallback, useEffect, useState } from "react";
import {
  CONTENT_LIST_ORDER,
  type ContentListOrder,
  isValidStoredContentListOrder,
} from "@/lib/constants/contentListOrder";
import { getLocalString, removeLocalKey, setLocalString, STORAGE_KEYS } from "@/lib/storage";

type OrderPreferenceStorageKey =
  | typeof STORAGE_KEYS.prefExerciseOrder
  | typeof STORAGE_KEYS.prefChallengeOrder;

/**
 * Hydrates list sort preference from localStorage after mount; persists on change.
 */
export function useContentListOrderPreference(storageKey: OrderPreferenceStorageKey) {
  const [orderFilter, setOrderFilter] = useState<ContentListOrder>(CONTENT_LIST_ORDER.RANDOM);

  useEffect(() => {
    const raw = getLocalString(storageKey);
    if (isValidStoredContentListOrder(raw)) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional post-hydration sync
      setOrderFilter(raw);
    }
  }, [storageKey]);

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
