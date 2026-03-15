# Lot C2 - Distributed Rate Limit

> Date: 14/03/2026
> Iteration: C - Production Hardening
> Priorite: P1 anti-abus
> Statut: **terminé** — voir `PILOTAGE_CURSOR_PRODUCTION_HARDENING_C2_DISTRIBUTED_RATE_LIMIT_REPORT_2026-03-14.md`

## 1. Mission

Remplacer les protections anti-abus en memoire mono-instance par une strategie
distribuee defendable en production.

## 2. Contexte actuel prouve

Les modules suivants annoncent eux-memes leur limite:

- `app/utils/rate_limit.py`
- `app/utils/rate_limiter.py`

Commentaires explicites:

- "stockage en memoire - inefficace en multi-instances"
- "peut etre migre vers Redis pour production"

Le scope touche notamment:

- auth (`login`, `forgot-password`, `resend-verification`)
- chat public
- generation IA challenge

## 3. Faux positifs a eviter

- confondre "rate limit existe" et "rate limit robuste en prod"
- ouvrir en meme temps observabilite, quotas business et refactor auth
- garder deux systemes paralleles apres le lot

## 4. Risque production exact

Impact concret:

- contournement des quotas entre instances
- exposition au cout OpenAI sur les endpoints publics IA
- anti-bruteforce faible si le trafic est distribue

## 5. Decision d'architecture imposee

Decision cible:

- store distribue Redis
- cle de quota par route + IP et/ou user
- interface unifiee pour les appels auth/chat/IA

Le lot doit sortir avec:

- un seul mecanisme principal
- une transition claire depuis les deux implementations memoire actuelles

## 6. Ce qui est mal place

- deux implementations separees pour le rate limit
- stockage purement en memoire sur un perimetre prod

## 7. Ce qui est duplique ou fragile

- cles de quotas heterogenes
- messages et logique disperses
- absence de garantie multi-instance

## 8. Decoupage cible

- un composant rate limit distribue central
- adapteurs minces pour:
  - auth decorators
  - chat
  - generation IA challenge

## 9. Exemples avant / apres

### Avant

```py
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
```

### Apres

```py
allowed = distributed_rate_limit.check(
    scope="chat",
    key=f"ip:{client_ip}",
    limit=15,
    window_seconds=60,
)
```

## 10. Fichiers a lire avant toute modification

- `D:\\Mathakine\\app\\utils\\rate_limit.py`
- `D:\\Mathakine\\app\\utils\\rate_limiter.py`
- `D:\\Mathakine\\server\\handlers\\chat_handlers.py`
- `D:\\Mathakine\\server\\middleware.py`
- handlers auth concernes

## 11. Scope autorise

- les deux modules rate limit
- handlers/auth calls concernes
- config Redis strictement necessaire
- tests auth/chat/IA concernes

## 12. Scope interdit

- refactor auth large
- refonte observabilite complete
- changement de logique produit
- chantier diagnostic

## 13. Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. batterie auth/chat/ia ciblee
4. relancer exactement la meme batterie
5. `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py`
6. `black app/ server/ tests/ --check`
7. `isort app/ server/ --check-only --diff`

## 14. Exigences de validation

- prouver que le quota ne repose plus uniquement sur de la memoire locale
- prouver quel composant remplace l'autre
- lister les routes reellement protegees par le nouveau chemin

## 15. Stop conditions

- si Redis n'est pas disponible dans l'environnement projet
- si le lot devient un chantier infra global
- dans ce cas: STOP, documenter, ne pas improviser

## 16. Format de compte-rendu final

1. Fichiers modifies
2. Fichiers runtime modifies
3. Fichiers de test modifies
4. Routes reellement touchees
5. Strategie distribuee retenue
6. Perimetre anti-abus reel couvert
7. Ce qui a ete prouve
8. Ce qui n'a pas ete prouve
9. Resultat run 1
10. Resultat run 2
11. Resultat full suite
12. Resultat black
13. Resultat isort
14. Risques residuels
15. GO / NO-GO

