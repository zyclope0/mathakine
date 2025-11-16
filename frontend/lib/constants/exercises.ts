/**
 * Constantes pour les types d'exercices
 */
export const EXERCISE_TYPES = {
  ADDITION: 'addition',
  SUBTRACTION: 'soustraction',
  MULTIPLICATION: 'multiplication',
  DIVISION: 'division',
  MIXTE: 'mixte',
  FRACTIONS: 'fractions',
  GEOMETRIE: 'geometrie',
  TEXTE: 'texte',
  DIVERS: 'divers',
} as const;

export type ExerciseType = (typeof EXERCISE_TYPES)[keyof typeof EXERCISE_TYPES];

export const EXERCISE_TYPE_DISPLAY: Record<ExerciseType, string> = {
  [EXERCISE_TYPES.ADDITION]: 'Addition',
  [EXERCISE_TYPES.SUBTRACTION]: 'Soustraction',
  [EXERCISE_TYPES.MULTIPLICATION]: 'Multiplication',
  [EXERCISE_TYPES.DIVISION]: 'Division',
  [EXERCISE_TYPES.MIXTE]: 'Mixte',
  [EXERCISE_TYPES.FRACTIONS]: 'Fractions',
  [EXERCISE_TYPES.GEOMETRIE]: 'Géométrie',
  [EXERCISE_TYPES.TEXTE]: 'Texte',
  [EXERCISE_TYPES.DIVERS]: 'Divers',
};

/**
 * Constantes pour les niveaux de difficulté
 */
export const DIFFICULTY_LEVELS = {
  INITIE: 'initie',
  PADAWAN: 'padawan',
  CHEVALIER: 'chevalier',
  MAITRE: 'maitre',
} as const;

export type DifficultyLevel = (typeof DIFFICULTY_LEVELS)[keyof typeof DIFFICULTY_LEVELS];

export const DIFFICULTY_DISPLAY: Record<DifficultyLevel, string> = {
  [DIFFICULTY_LEVELS.INITIE]: 'Initié',
  [DIFFICULTY_LEVELS.PADAWAN]: 'Padawan',
  [DIFFICULTY_LEVELS.CHEVALIER]: 'Chevalier',
  [DIFFICULTY_LEVELS.MAITRE]: 'Maître',
};

/**
 * Couleurs CSS pour les badges de difficulté
 * Utilisables dans tous les composants d'exercices
 */
export const DIFFICULTY_COLORS: Record<DifficultyLevel, string> = {
  [DIFFICULTY_LEVELS.INITIE]: 'bg-green-500/20 text-green-400 border-green-500/30 dark:bg-green-500/30 dark:text-green-300 dark:border-green-500/40',
  [DIFFICULTY_LEVELS.PADAWAN]: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30 dark:bg-yellow-500/30 dark:text-yellow-300 dark:border-yellow-500/40',
  [DIFFICULTY_LEVELS.CHEVALIER]: 'bg-orange-500/20 text-orange-400 border-orange-500/30 dark:bg-orange-500/30 dark:text-orange-300 dark:border-orange-500/40',
  [DIFFICULTY_LEVELS.MAITRE]: 'bg-red-500/20 text-red-400 border-red-500/30 dark:bg-red-500/30 dark:text-red-300 dark:border-red-500/40',
};

/**
 * Constantes pour les types de défis logiques
 */
export const CHALLENGE_TYPES = {
  SEQUENCE: 'sequence',
  PATTERN: 'pattern',
  VISUAL: 'visual',
  PUZZLE: 'puzzle',
  DEDUCTION: 'deduction',
  SPATIAL: 'spatial',
  PROBABILITY: 'probability',
  GRAPH: 'graph',
  CODING: 'coding',
  CHESS: 'chess',
  CUSTOM: 'custom',
} as const;

export type ChallengeType = (typeof CHALLENGE_TYPES)[keyof typeof CHALLENGE_TYPES];

