# Analyse — Génération IA des exercices

> **Date :** Fév. 2026  
> **Type :** Analyse technique  
> **Contexte :** Bug identifié sur l'exercice fractions "cristaux 120" (réponse erronée 30 au lieu de 20)

---

## 1. Pipeline de génération

| Source | Méthode | Déterministe |
|--------|---------|--------------|
| `generate_ai_exercise` | Logique Python (exercise_generator.py) | Oui |
| `generate_ai_exercise_stream` | OpenAI API (GPT) | Non |

L'exercice "L'Alliance des Fractions" (120 cristaux, moitié rouges, tiers bleus) est généré par **generate_ai_exercise_stream** (OpenAI), pas par le générateur déterministe.

---

## 2. Bug identifié (cristaux 120)

**Problème :** La question demande combien de cristaux sont ni rouges ni bleus.
- Rouges : 120 × 1/2 = 60
- Bleus : 120 × 1/3 = 40
- Total coloré : 100
- **Réponse correcte : 20** (120 - 100)

**Erreur IA :** L'exercice indiquait 30 comme bonne réponse, avec une explication contradictoire (calcul initial correct 20, puis "correction" fictive vers 30).

**Correction :** Script `scripts/fix_fraction_cristaux_exercise.py`
```bash
python scripts/fix_fraction_cristaux_exercise.py --execute
```

---

## 3. Mesures de prévention

### 3.1 Prompt renforcé (appliqué)

Règle 6 ajoutée au prompt système (exercise_handlers.py) :
> Pour les problèmes de fractions (ex: "moitié de X", "tiers de Y") : calcule d'abord chaque partie, additionne, puis soustrais du total. La réponse doit être cohérente avec ces calculs. Ne pas inventer d'"erreur" ou de "correction" fictive dans l'explication.

### 3.2 Pistes futures

| Piste | Effort | Impact |
|------|--------|--------|
| Validation post-génération | Moyen | Détecte incohérences pour problèmes à structure connue |
| Double-check par un second appel IA | Faible | Vérifier "Est-ce que correct_answer correspond aux calculs de l'explication ?" |
| Flag manuel "exercice à revoir" | Faible | Permettre aux utilisateurs de signaler des erreurs |
| Tests unitaires sur exercices seed | Faible | Garantir que les exercices prédéfinis sont corrects |

---

## 4. Fichiers concernés

- `server/handlers/exercise_handlers.py` — Prompt système (lignes 696-728)
- `server/exercise_generator.py` — Génération déterministe (fractions, géométrie, etc.)
- `scripts/fix_fraction_cristaux_exercise.py` — Correction exercice cristaux
