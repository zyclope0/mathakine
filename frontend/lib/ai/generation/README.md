# Génération IA (exercices / défis) — couche client

## Rôles

| Couche                  | Fichiers                                                                          | Rôle                                                                                                                                                                    |
| ----------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **POST + en-tetes SSE** | `postAiGenerationSse.ts`                                                          | `fetch` POST vers `/api/.../generate-ai-stream` (`Accept`, CSRF si requis) + mapping des erreurs de requete (`csrf_token_missing`, `http_401`, `http_403`, `http_backend`). |
| **Lecture flux**        | `../utils/ssePostStream.ts`                                                       | Parse `data: {...}` (déjà en place, inchangé ici).                                                                                                                      |
| **Dispatch événements** | `dispatchExerciseAiSseEvent.ts`, `dispatchChallengeAiSseEvent.ts`                 | Interprète `type` (`status`, `warning`, `exercise`/`challenge`, `error`, `done`) ; toasts ; **ne pose l’état « ressource créée » que si un `id` persisté est présent**. |
| **Normalisation id**    | `normalizeResourceId.ts`                                                          | `number` ou chaîne numérique → `number` pour les CTA (`/exercises/:id`, `/challenge/:id`).                                                                              |
| **Hooks**               | `hooks/useAIExerciseGenerator.ts`, `hooks/useAIChallengeGenerator.ts`             | État UI (`isGenerating`, texte stream, ressource), annulation, orchestration.                                                                                           |
| **Composants**          | `AIGeneratorBase`, `AIGenerator` (exercise/challenge), `UnifiedExerciseGenerator` | Rendu + callbacks ; CTA « Voir » uniquement si `generatedItem.id` défini (pas couplé au transport).                                                                     |

## Echecs de requete avant lecture SSE

`postAiGenerationSse.ts` ne laisse plus les hooks re-decoder a la main les erreurs HTTP/proxy les plus courantes.

- CSRF absent ou vide cote navigateur -> `AiGenerationRequestError("csrf_token_missing")`, sans `fetch`
- backend `401` -> `AiGenerationRequestError("http_401")`
- backend `403` ou `EMAIL_VERIFICATION_REQUIRED` -> `AiGenerationRequestError("http_403")`
- autre backend non-OK -> `AiGenerationRequestError("http_backend")`

Le mapping toast utilisateur est centralise dans `getAiGenerationRequestErrorToast.ts`. Les hooks generation n'ont plus a faire de parsing JSON ad hoc pour ces cas.

## Tests

- `frontend/__tests__/unit/ai-generation/postAiGenerationSse.test.ts`
  - CSRF absent / vide
  - succes avec en-tete CSRF
  - `401`, `403`, `500`
  - code backend `EMAIL_VERIFICATION_REQUIRED`
  - mapping des toasts i18n

## CTA fin de génération

Les boutons « Voir l’exercice / le défi » dépendent de `AIGeneratedItem.id` (ou équivalent dans `UnifiedExerciseGenerator`), alimenté après dispatch **uniquement** en cas de persistance réussie côté API.

Import historique : `@/lib/challenges/dispatchChallengeAiSseEvent` réexporte encore le module pour compatibilité.
