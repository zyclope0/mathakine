# Génération IA (exercices / défis) — couche client

## Rôles

| Couche                  | Fichiers                                                                          | Rôle                                                                                                                                                                    |
| ----------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **POST + en-têtes SSE** | `postAiGenerationSse.ts`                                                          | `fetch` POST vers `/api/.../generate-ai-stream` (cookies, CSRF, `Accept`).                                                                                              |
| **Lecture flux**        | `../utils/ssePostStream.ts`                                                       | Parse `data: {...}` (déjà en place, inchangé ici).                                                                                                                      |
| **Dispatch événements** | `dispatchExerciseAiSseEvent.ts`, `dispatchChallengeAiSseEvent.ts`                 | Interprète `type` (`status`, `warning`, `exercise`/`challenge`, `error`, `done`) ; toasts ; **ne pose l’état « ressource créée » que si un `id` persisté est présent**. |
| **Normalisation id**    | `normalizeResourceId.ts`                                                          | `number` ou chaîne numérique → `number` pour les CTA (`/exercises/:id`, `/challenge/:id`).                                                                              |
| **Hooks**               | `hooks/useAIExerciseGenerator.ts`, `hooks/useAIChallengeGenerator.ts`             | État UI (`isGenerating`, texte stream, ressource), annulation, orchestration.                                                                                           |
| **Composants**          | `AIGeneratorBase`, `AIGenerator` (exercise/challenge), `UnifiedExerciseGenerator` | Rendu + callbacks ; CTA « Voir » uniquement si `generatedItem.id` défini (pas couplé au transport).                                                                     |

## CTA fin de génération

Les boutons « Voir l’exercice / le défi » dépendent de `AIGeneratedItem.id` (ou équivalent dans `UnifiedExerciseGenerator`), alimenté après dispatch **uniquement** en cas de persistance réussie côté API.

Import historique : `@/lib/challenges/dispatchChallengeAiSseEvent` réexporte encore le module pour compatibilité.
