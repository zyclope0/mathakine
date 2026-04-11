"use client";

export function LeaderboardSectionSeparator({ label }: { label: string }) {
  return (
    <li className="leaderboard-section-separator list-none" aria-hidden="true">
      {label}
    </li>
  );
}
