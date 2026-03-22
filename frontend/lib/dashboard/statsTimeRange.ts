import type { TimeRange } from "@/hooks/useUserStats";

/** Maps API/query time range to `dashboard.timeRange.*` message keys. */
export function statsTimeRangeToMessageKey(
  timeRange: TimeRange
): "7days" | "30days" | "90days" | "all" {
  if (timeRange === "7") return "7days";
  if (timeRange === "30") return "30days";
  if (timeRange === "90") return "90days";
  return "all";
}
