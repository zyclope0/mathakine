import type { Variants } from "framer-motion";

export function springForRank(rank: number) {
  if (rank <= 3) return { stiffness: 180, damping: 14 };
  if (rank <= 10) return { stiffness: 220, damping: 18 };
  return { stiffness: 260, damping: 22 };
}

export function buildLeaderboardListVariants(shouldReduceMotion: boolean): Variants {
  return shouldReduceMotion
    ? { hidden: {}, show: {} }
    : {
        hidden: { opacity: 0 },
        show: {
          opacity: 1,
          transition: { staggerChildren: 0.04, delayChildren: 0.02 },
        },
      };
}

export function buildLeaderboardRowVariants(shouldReduceMotion: boolean): Variants {
  return shouldReduceMotion
    ? { hidden: { opacity: 0 }, show: { opacity: 1 } }
    : {
        hidden: { opacity: 0, y: 12, scale: 0.99 },
        show: (rank: number) => ({
          opacity: 1,
          y: 0,
          scale: 1,
          transition: {
            type: "spring",
            ...springForRank(typeof rank === "number" ? rank : 99),
          },
        }),
      };
}
