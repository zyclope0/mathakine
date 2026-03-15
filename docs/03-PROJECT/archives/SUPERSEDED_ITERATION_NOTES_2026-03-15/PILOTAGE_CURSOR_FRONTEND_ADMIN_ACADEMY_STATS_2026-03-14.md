# Quick Win Produit - Admin Academy Stats - 2026-03-14

## Statut

Implante.

## Objectif

Exploiter `GET /api/exercises/stats` dans l'admin sans ouvrir une nouvelle page
ni dupliquer la logique du widget home.

## Scope applique

- `frontend/components/admin/AdminAcademyStatsSection.tsx`
- `frontend/app/admin/page.tsx`
- `frontend/__tests__/unit/components/admin/AdminAcademyStatsSection.test.tsx`

## Decisions d'implementation

- pas de nouvelle page `/admin/stats`
- pas de changement backend
- reutilisation du hook existant `useAcademyStats()`
- ajout d'une section sur la page admin overview existante

## Donnees affichees

- `academy_statistics.total_exercises`
- `academy_statistics.total_challenges`
- `academy_statistics.ai_generated`
- `global_performance.total_attempts`
- top 3 disciplines
- top 3 rangs

## Pourquoi ce choix

- valeur visible immediate cote admin
- zero duplication de logique de fetch
- pas de refactor du widget home
- blast radius faible

## Hors scope

- nouvelle page admin dediee
- nouveaux endpoints backend
- analytics admin plus profondes
- duplication du composant `AcademyStatsWidget`
