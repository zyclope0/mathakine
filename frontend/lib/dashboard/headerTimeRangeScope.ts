/**
 * Dashboard header time range applies to {@link useUserStats} data (export, some charts).
 * It is not a global filter for every tab; hide the control where it would mislead users.
 */
export function shouldShowHeaderTimeRange(activeTab: string): boolean {
  return activeTab === "overview" || activeTab === "profile";
}
