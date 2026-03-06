# F04 — Révisions espacées (algorithme SM-2)

> **Référence technique** — Spécification pour implémentation future  
> **Date :** 06/03/2026  
> **Statut :** Non implémenté (spec)  
> **Source :** [ROADMAP_FONCTIONNALITES §F04](ROADMAP_FONCTIONNALITES.md)

---

## 1. Vue d'ensemble

F04 implémente un système de révisions espacées basé sur l'algorithme SM-2 (Wozniak, 1987) pour optimiser la rétention à long terme des compétences acquises.

**Fondements scientifiques :**
- Ebbinghaus (1885) — Courbe de l'oubli : 70% oublié en 24h, 90% en une semaine
- Cepeda et al. (2006) — Méta-analyse 317 études : pratique espacée +200% vs massée
- Kornell & Bjork (2008) — Spacing + interleaving en mathématiques (g = 0.43)
- SM-2 : fondement de SuperMemo, Anki, DuoLingo

---

## 2. Algorithme SM-2 adapté

```
Intervalles de révision :
- 1ère révision : J+1
- 2ème révision : J+3
- 3ème révision : J+7
- Suivantes : intervalle × ease_factor

Ajustement ease_factor (EF, init 2.5) :
- Réponse correcte rapide (qualité 4-5) : EF + 0.1
- Réponse correcte lente (qualité 3) : EF inchangé
- Réponse incorrecte (qualité 0-2) : EF − 0.2, retour J+1
```

**Qualité** : 0–5 (échelle utilisateur ou dérivée de temps de réponse + correct/incorrect).

---

## 3. Modèle de données prévu

```sql
spaced_repetition_items (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  exercise_id INT REFERENCES exercises(id) ON DELETE SET NULL,
  -- Ou : challenge_id, concept_id selon granularité choisie
  ease_factor FLOAT DEFAULT 2.5,
  interval_days INT DEFAULT 1,
  next_review_date DATE NOT NULL,
  repetition_count INT DEFAULT 0,
  last_quality INT,  -- 0-5
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)
```

**Granularité à trancher** : par exercice individuel, par concept (type + difficulté), ou par item généré (ex. ID temporaire). Impact sur la table et les jointures.

---

## 4. Intégration prévue

- **Après chaque tentative** : mise à jour ou création de l'item SR (qualité dérivée de correct/incorrect + temps)
- **Widget dashboard** : "Révisions du jour" — liste des items dont `next_review_date = TODAY`
- **Dépendances** : Profite du diagnostic (F03) pour prioriser les types faibles ; prépare F23 (exercices adaptatifs SR+IA)

---

## 5. Effort estimé

1–2 semaines (migration + service + UI widget)

---

## 6. Références

- [ROADMAP_FONCTIONNALITES §F04](ROADMAP_FONCTIONNALITES.md)
- [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) — Révisions espacées dans le parcours utilisateur
