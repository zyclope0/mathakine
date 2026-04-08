/**
 * Shared types for ChallengeSolver command bar subcomponents (FFI-L18B).
 */

export type ChallengeSolverCommandBarT = (
  key: string,
  values?: Record<string, string | number>
) => string;
