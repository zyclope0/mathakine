/**
 * Constantes pour les types de défis logiques
 */
export const CHALLENGE_TYPES = {
  SEQUENCE: 'sequence',
  PATTERN: 'pattern',
  VISUAL: 'visual',
  PUZZLE: 'puzzle',
  RIDDLE: 'riddle',
  DEDUCTION: 'deduction',
  SPATIAL: 'spatial',
  PROBABILITY: 'probability',
  GRAPH: 'graph',
  CODING: 'coding',
  CHESS: 'chess',
  CUSTOM: 'custom',
} as const;

export type ChallengeType = (typeof CHALLENGE_TYPES)[keyof typeof CHALLENGE_TYPES];

export const CHALLENGE_TYPE_DISPLAY: Record<ChallengeType, string> = {
  [CHALLENGE_TYPES.SEQUENCE]: 'Séquence',
  [CHALLENGE_TYPES.PATTERN]: 'Motif',
  [CHALLENGE_TYPES.VISUAL]: 'Visuel',
  [CHALLENGE_TYPES.PUZZLE]: 'Puzzle',
  [CHALLENGE_TYPES.RIDDLE]: 'Énigme',
  [CHALLENGE_TYPES.DEDUCTION]: 'Déduction',
  [CHALLENGE_TYPES.SPATIAL]: 'Spatial',
  [CHALLENGE_TYPES.PROBABILITY]: 'Probabilité',
  [CHALLENGE_TYPES.GRAPH]: 'Graphe',
  [CHALLENGE_TYPES.CODING]: 'Codage',
  [CHALLENGE_TYPES.CHESS]: 'Échecs',
  [CHALLENGE_TYPES.CUSTOM]: 'Personnalisé',
};

/**
 * Constantes pour les groupes d'âge
 */
export const AGE_GROUPS = {
  ENFANT: 'enfant',
  ADOLESCENT: 'adolescent',
  ADULTE: 'adulte',
  AGE_9_12: '9-12',
  AGE_12_13: '12-13',
  AGE_13_PLUS: '13+',
  GROUP_10_12: '10-12',
  GROUP_13_15: '13-15',
  ALL_AGES: 'all',
} as const;

export type AgeGroup = (typeof AGE_GROUPS)[keyof typeof AGE_GROUPS];

export const AGE_GROUP_DISPLAY: Record<AgeGroup, string> = {
  [AGE_GROUPS.ENFANT]: 'Enfant',
  [AGE_GROUPS.ADOLESCENT]: 'Adolescent',
  [AGE_GROUPS.ADULTE]: 'Adulte',
  [AGE_GROUPS.AGE_9_12]: '9 à 12 ans',
  [AGE_GROUPS.AGE_12_13]: '12 à 13 ans',
  [AGE_GROUPS.AGE_13_PLUS]: '13 ans et plus',
  [AGE_GROUPS.GROUP_10_12]: '10 à 12 ans',
  [AGE_GROUPS.GROUP_13_15]: '13 à 15 ans',
  [AGE_GROUPS.ALL_AGES]: 'Tous âges',
};

/**
 * Couleurs CSS pour les badges de groupe d'âge
 * Utilisables dans tous les composants de challenges
 */
export const AGE_GROUP_COLORS: Record<string, string> = {
  '9-12': 'bg-green-500/20 text-green-300 border-green-500/30',
  '10-12': 'bg-green-500/20 text-green-300 border-green-500/30',
  '12-13': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  '13-15': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  '13+': 'bg-red-500/20 text-red-300 border-red-500/30',
  'all': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  // Fallback pour les autres groupes d'âge
  'enfant': 'bg-green-500/20 text-green-300 border-green-500/30',
  'adolescent': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  'adulte': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  // Support des clés PostgreSQL (GROUP_10_12, GROUP_13_15)
  'GROUP_10_12': 'bg-green-500/20 text-green-300 border-green-500/30',
  'GROUP_13_15': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
};

/**
 * Mapping des valeurs de groupe d'âge depuis la base de données vers les clés d'affichage
 * Gère les variantes : valeurs ('10-12'), clés ('GROUP_10_12'), etc.
 */
const AGE_GROUP_VALUE_MAP: Record<string, AgeGroup> = {
  // Valeurs directes
  '9-12': AGE_GROUPS.AGE_9_12,
  '10-12': AGE_GROUPS.GROUP_10_12,
  '12-13': AGE_GROUPS.AGE_12_13,
  '13-15': AGE_GROUPS.GROUP_13_15,
  '13+': AGE_GROUPS.AGE_13_PLUS,
  'all': AGE_GROUPS.ALL_AGES,
  // Clés PostgreSQL (si retournées par la BDD)
  'GROUP_10_12': AGE_GROUPS.GROUP_10_12,
  'GROUP_13_15': AGE_GROUPS.GROUP_13_15,
  'AGE_9_12': AGE_GROUPS.AGE_9_12,
  'AGE_12_13': AGE_GROUPS.AGE_12_13,
  'AGE_13_PLUS': AGE_GROUPS.AGE_13_PLUS,
  'ALL_AGES': AGE_GROUPS.ALL_AGES,
  // Valeurs textuelles
  'enfant': AGE_GROUPS.ENFANT,
  'adolescent': AGE_GROUPS.ADOLESCENT,
  'adulte': AGE_GROUPS.ADULTE,
};

/**
 * Normalise une valeur de groupe d'âge depuis la BDD vers une clé AgeGroup valide
 */
export function normalizeAgeGroup(value: string | null | undefined): AgeGroup {
  if (!value) return AGE_GROUPS.ALL_AGES;
  
  // Si c'est déjà une clé valide, la retourner directement
  if (value in AGE_GROUP_DISPLAY) {
    return value as AgeGroup;
  }
  
  // Sinon, utiliser le mapping
  return AGE_GROUP_VALUE_MAP[value] || AGE_GROUPS.ALL_AGES;
}

/**
 * Obtient le libellé d'affichage pour un groupe d'âge
 * Gère automatiquement la normalisation
 */
export function getAgeGroupDisplay(value: string | null | undefined): string {
  const normalized = normalizeAgeGroup(value);
  return AGE_GROUP_DISPLAY[normalized] || 'Tous âges';
}

/**
 * Obtient la couleur CSS pour un groupe d'âge
 * Gère automatiquement la normalisation
 */
export function getAgeGroupColor(value: string | null | undefined): string {
  if (!value) return AGE_GROUP_COLORS['all'];
  
  // Essayer directement avec la valeur brute (pour les cas comme '10-12', 'GROUP_10_12', etc.)
  if (value in AGE_GROUP_COLORS) {
    return AGE_GROUP_COLORS[value];
  }
  
  // Normaliser et utiliser la valeur normalisée
  const normalized = normalizeAgeGroup(value);
  const normalizedValue = AGE_GROUPS[normalized as keyof typeof AGE_GROUPS] || normalized;
  
  // Essayer avec la valeur normalisée
  if (normalizedValue in AGE_GROUP_COLORS) {
    return AGE_GROUP_COLORS[normalizedValue];
  }
  
  // Fallback
  return AGE_GROUP_COLORS['all'];
}

