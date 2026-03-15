# Delta restant - Post iteration backend exercise auth user - 2026-03-09

## Resume

L'iteration backend `exercise/auth/user` est cloturee et stabilisee.
Le delta restant n'est plus un delta de correction critique : il concerne surtout
des reliquats UX/doc et des sujets de finition hors scope.

## Ce qui reste a faire

### 1. UX frontend auth au refresh (`F36`)
- **Statut :** non bloquant
- **Symptome :** bref flash visuel au refresh ou pendant le bootstrap auth
- **Lecture actuelle :** la session backend tient ; le sujet est cote frontend (`ProtectedRoute`, bootstrap auth, sync-cookie/check-cookie)
- **Verification 2026-03-14 :** non reproduit sur l'etat actuel du code ; aucune correction appliquee
- **Action rentable :** reouvrir un mini lot frontend dedie seulement si le flash devient genant ou s'accompagne d'une redirection parasite

### 2. Documentation de second rang a resynchroniser
- **Statut :** moyen
- **Perimetre :** documents secondaires encore susceptibles de mentionner l'ancienne organisation backend
- **Action rentable :** garder alignes les documents actifs si de nouveaux quick wins frontend/admin sont ouverts

### 3. Observabilite auth a surveiller
- **Statut :** faible
- **Constat :** le rejet d'un ancien refresh token apres reset/change password logge un warning utile
- **Action rentable :** ne rien changer tant que le log n'apparait pas en boucle ; requalifier le niveau de log plus tard seulement si le bruit devient excessif

## Ce qui ne reste plus a faire dans ce delta
- alignement reset password / revocation sessions : ferme
- alignement changement de mot de passe / revocation sessions : ferme
- recablage export RGPD : ferme
- boundaries `exercise`, `auth`, `user` : fermees pour cette iteration

## Note d'actualisation

Les iterations backend `challenge/admin/badge`, `Runtime Truth` et
`Contracts / Hardening` ont depuis ete cloturees. Ce document reste utile comme
trace du delta post `exercise/auth/user`, mais ne doit plus etre interprete
comme un plan actif de suite.
