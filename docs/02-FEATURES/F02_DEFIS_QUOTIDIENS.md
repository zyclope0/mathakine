# F02 — Défis quotidiens (Daily Challenges)

> **Référence technique** — Contexte complet pour développeurs et prompts IA  
> **Date :** 06/03/2026  
> **Statut :** Implémenté (Mars 2026)  
> **Source :** [ROADMAP_FONCTIONNALITES §F02](ROADMAP_FONCTIONNALITES.md)

---

## 1. Vue d'ensemble

F02 propose 3 objectifs quotidiens à l'utilisateur pour encourager la pratique distribuée et le retour quotidien. Les défis sont optionnels, sans punition si manqués (SDT — Deci & Ryan).

**Fondements scientifiques :**
- Cepeda et al. (2006) — Pratique distribuée : rétention supérieure à la pratique massée (d = 0.46-0.71)
- Deci & Ryan (2000) — SDT : défis optionnels adaptés soutiennent la compétence sans pression externe

---

## 2. Types de défis

| Type | Description | Exemple | Bonus XP |
|------|-------------|---------|----------|
| `volume_exercises` | N exercices quelconques | 3 exercices | 10 |
| `specific_type` | N exercices d'un type donné | 2 exercices de Soustraction | 15 |
| `logic_challenge` | N défis logiques | 1 défi logique | 20 |

**Types d'exercices pour specific_type :** addition, soustraction, multiplication, division (alignés diagnostic F03).

---

## 3. Modèle de données — Table `daily_challenges`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | int | PK |
| `user_id` | int | FK users.id (CASCADE) |
| `date` | date | Date du défi (YYYY-MM-DD) |
| `challenge_type` | str | volume_exercises \| specific_type \| logic_challenge |
| `metadata` | JSONB | Pour specific_type : `{"exercise_type": "addition"}` |
| `target_count` | int | Objectif (ex: 3) |
| `completed_count` | int | Progression (ex: 1) |
| `status` | str | pending \| completed \| expired |
| `bonus_points` | int | XP bonus à la complétion |
| `created_at` | timestamp | Création |
| `completed_at` | timestamp | Date de complétion (null si pending) |

**Index :** `ix_daily_challenges_user_date` sur (user_id, date)

---

## 4. Endpoints API

| Méthode | Endpoint | Auth | Body / Params |
|---------|----------|------|---------------|
| GET | `/api/daily-challenges` | Oui (full_access) | — |

**Réponse :**
```json
{
  "challenges": [
    {
      "id": 1,
      "date": "2026-03-06",
      "challenge_type": "volume_exercises",
      "metadata": {},
      "target_count": 3,
      "completed_count": 1,
      "status": "pending",
      "bonus_points": 10
    }
  ]
}
```

**Comportement :** Crée automatiquement les 3 défis du jour s'ils n'existent pas (lazy creation).

---

## 5. Mise à jour de la progression

La progression n'est **pas** mise à jour par le endpoint GET. Elle est déclenchée par les flux de soumission métier, puis persistée par leur point d'orchestration transactionnel :

| Point d'entrée | Service | Défis mis à jour |
|----------------|---------|------------------|
| `submit_answer` (exercices) | `app/services/exercise_service.py` | volume_exercises, specific_type |
| `submit_challenge_answer` (défis logiques) | `app/services/logic_challenge_service.py` | logic_challenge |

**Fichiers :**
- `app/services/exercise_service.py` → `record_exercise_completed()`
- `app/services/logic_challenge_service.py` → `record_logic_challenge_completed()`

**Important :**

- les handlers HTTP restent des adaptateurs de transport
- la soumission d'exercice et la soumission de défi logique portent chacune leur commit final dans le service d'orchestration
- les mises à jour `daily challenges` sont appelées en side effect best effort depuis ces services, sans reprendre la main sur le commit global

---

## 6. Fichiers impliqués

| Rôle | Fichier |
|------|---------|
| Modèle | `app/models/daily_challenge.py` |
| Service | `app/services/progress/daily_challenge_service.py` |
| Handlers | `server/handlers/daily_challenge_handlers.py` |
| Routes | `server/routes/users.py` (déclaration) |
| Migration | `migrations/versions/20260307_add_daily_challenges.py` |

---

## 7. Expiration

Les défis des jours passés en `pending` peuvent être marqués `expired` via `expire_past_daily_challenges(db)`. À appeler périodiquement (cron ou tâche planifiée).

---

## 8. Références

- **Widget frontend :** [F02_DAILY_CHALLENGES_WIDGET.md](../06-WIDGETS/F02_DAILY_CHALLENGES_WIDGET.md)
- **Refactor dashboard :** [REFACTOR_DASHBOARD_2026-03.md](../03-PROJECT/REFACTOR_DASHBOARD_2026-03.md)
