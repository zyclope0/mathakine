# Delta restant - Post iteration backend exercise auth user - 2026-03-09

## Resume

L'iteration backend `exercise/auth/user` est cloturee et stabilisee.
Le delta restant n'est plus un delta de correction critique : il concerne surtout des reliquats UX/doc et la prochaine iteration backend.

## Ce qui reste a faire

### 1. UX frontend auth au refresh (`F36`)
- **Statut :** non bloquant
- **Symptome :** bref flash visuel au refresh ou pendant le bootstrap auth
- **Lecture actuelle :** la session backend tient ; le sujet est cote frontend (`ProtectedRoute`, bootstrap auth, sync-cookie/check-cookie)
- **Action rentable :** ouvrir un mini lot frontend dedie seulement si le flash devient genant ou s'accompagne d'une redirection parasite

### 2. Documentation de second rang a resynchroniser
- **Statut :** moyen
- **Perimetre :** documents non critiques encore susceptibles de mentionner l'ancienne organisation `server/exercise_generator*` ou l'ancienne cartographie des handlers
- **Action rentable :** verifier ensuite `docs/00-REFERENCE/ARCHITECTURE.md` et les guides techniques secondaires si on veut une coherence documentaire totale

### 3. Prochaine iteration backend
- **Statut :** priorite naturelle de suite
- **Domaines recommandes :** `challenge`, `admin`, `badge`
- **Motif :** ce sont maintenant les plus gros hotspots restants en separation controller/service/repository, taille de services et lisibilite d'orchestration
- **Points chauds connus :** `challenge_validator.py`, `badge_service.py`, `admin_content_service.py`, `admin_stats_service.py`

### 4. Observabilite auth a surveiller
- **Statut :** faible
- **Constat :** le rejet d'un ancien refresh token apres reset/change password logge un warning utile
- **Action rentable :** ne rien changer tant que le log n'apparait pas en boucle ; requalifier le niveau de log plus tard seulement si le bruit devient excessif

## Ce qui ne reste plus a faire dans ce delta
- alignement reset password / revocation sessions : ferme
- alignement changement de mot de passe / revocation sessions : ferme
- recablage export RGPD : ferme
- boundaries `exercise`, `auth`, `user` : fermees pour cette iteration

## Recommendation
- publier / commit / push la version si les fichiers finaux sont bien stages
- ouvrir ensuite une nouvelle iteration backend separee pour `challenge/admin/badge`
