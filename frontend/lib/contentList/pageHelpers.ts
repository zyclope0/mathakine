import { CONTENT_LIST_ORDER, type ContentListOrder } from "@/lib/constants/contentListOrder";

export function contentListTotalPages(total: number, itemsPerPage: number): number {
  return Math.ceil(total / itemsPerPage) || 1;
}

export function hasActiveContentListFilters(params: {
  typeFilter: string;
  ageFilter: string;
  searchQuery: string;
  orderFilter: ContentListOrder;
  hideCompleted: boolean;
}): boolean {
  return (
    params.typeFilter !== "all" ||
    params.ageFilter !== "all" ||
    params.searchQuery.trim() !== "" ||
    params.orderFilter !== CONTENT_LIST_ORDER.RANDOM ||
    params.hideCompleted
  );
}

export function contentListAdvancedFilterActiveCount(
  typeFilter: string,
  ageFilter: string
): number {
  return (typeFilter !== "all" ? 1 : 0) + (ageFilter !== "all" ? 1 : 0);
}
