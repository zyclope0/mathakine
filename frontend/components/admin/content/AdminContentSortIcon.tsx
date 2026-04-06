"use client";

import { ChevronDown, ChevronUp } from "lucide-react";

export function AdminContentSortIcon({
  col,
  sort,
  order,
}: {
  col: string;
  sort: string;
  order: "asc" | "desc";
}) {
  if (sort !== col) return <ChevronDown className="ml-1 h-4 w-4 opacity-50" />;
  return order === "asc" ? (
    <ChevronUp className="ml-1 h-4 w-4" />
  ) : (
    <ChevronDown className="ml-1 h-4 w-4" />
  );
}
