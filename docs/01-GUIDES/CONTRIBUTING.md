# 🤝 CONTRIBUTING GUIDE - MATHAKINE

**Version** : 3.0.0  
**Date** : 09 fevrier 2026 (mise a jour)  
**Audience** : Contributeurs

---

## 👋 BIENVENUE

Merci de votre intérêt pour contribuer à **Mathakine** ! Ce guide vous aidera à contribuer efficacement.

---

## 🎯 TYPES DE CONTRIBUTIONS

Nous acceptons plusieurs types de contributions :

### 🐛 Bug Reports
- Signaler des bugs
- Fournir des logs/screenshots
- Proposer des solutions

### ✨ Feature Requests
- Proposer nouvelles fonctionnalités
- Améliorer l'UX
- Suggérer optimisations

### 📝 Documentation
- Corriger typos
- Améliorer explications
- Ajouter exemples

### 💻 Code Contributions
- Corriger bugs
- Implémenter features
- Refactoring
- Tests

---

## 🚀 WORKFLOW CONTRIBUTION

### Règle : tests systématiques

Pour toute **nouvelle fonctionnalité**, **implémentation** ou **correction** : challenger la pertinence de créer ou mettre à jour un test. Voir [TESTING.md § Règle projet](TESTING.md#regle-tests).

---

### 1. Fork & Clone

```bash
# 1. Fork sur GitHub
# Click "Fork" sur https://github.com/yourusername/mathakine

# 2. Clone votre fork
git clone https://github.com/VOTRE_USERNAME/mathakine.git
cd mathakine

# 3. Ajouter upstream
git remote add upstream https://github.com/yourusername/mathakine.git

# 4. Vérifier remotes
git remote -v
# origin    https://github.com/VOTRE_USERNAME/mathakine.git (fetch)
# upstream  https://github.com/yourusername/mathakine.git (fetch)
```

### 2. Créer une Branche

```bash
# Sync avec upstream
git checkout main
git pull upstream main

# Créer branche
git checkout -b feature/nom-feature
# OU
git checkout -b fix/nom-bug
```

### 3. Développer

```bash
# Installer dépendances
pip install -r requirements.txt
cd frontend && npm install

# Développer votre feature
# Suivre conventions (voir Development Guide)

# Tests
pytest tests/ -v
cd frontend && npm run test
```

### 4. Commit

```bash
# Ajouter fichiers
git add .

# Commit avec message conventionnel
git commit -m "feat: Add challenge filters

- Add filter by challenge_type
- Add filter by age_group
- Update API docs
"
```

**Format commits** :
```
type(scope): subject

body

footer
```

**Types** :
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction bug
- `docs`: Documentation
- `style`: Format code (pas de changement logique)
- `refactor`: Refactoring
- `test`: Ajout/modification tests
- `chore`: Tâches maintenance

**Exemples** :
```bash
git commit -m "feat(challenges): Add difficulty filter"
git commit -m "fix(auth): Correct token expiration"
git commit -m "docs(api): Update challenge endpoints"
git commit -m "test(challenges): Add unit tests for filters"
```

### 5. Push

```bash
# Push vers votre fork
git push origin feature/nom-feature
```

### 6. Pull Request

1. **Ouvrir PR** sur GitHub
2. **Remplir template** :
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation
   - [ ] Refactoring
   
   ## Checklist
   - [ ] Tests pass
   - [ ] Test ajouté/mis à jour si pertinent (feature, implémentation, fix) — voir [TESTING.md § Règle projet](TESTING.md#regle-tests)
   - [ ] Documentation updated
   - [ ] Code reviewed
   
   ## Screenshots
   (si applicable)
   ```

3. **Attendre review**
4. **Appliquer feedback**
5. **Merge**

---

## 📋 GUIDELINES

### Code Style

#### Backend (Python)
```python
# ✅ CORRECT
def get_challenges_by_type(
    db: Session,
    challenge_type: str,
    limit: int = 10
) -> list[Challenge]:
    """
    Récupérer challenges par type.
    
    Args:
        db: Session database
        challenge_type: Type de challenge (SEQUENCE, PATTERN, etc.)
        limit: Nombre max de résultats
    
    Returns:
        Liste de challenges
    """
    return db.query(Challenge)\
        .filter(Challenge.challenge_type == challenge_type)\
        .limit(limit)\
        .all()

# ❌ INCORRECT
def getChallenges(db, type):
    return db.query(Challenge).filter(Challenge.challenge_type == type).all()
```

**Regles** :
- `snake_case` pour functions/variables
- `PascalCase` pour classes
- `UPPER_SNAKE_CASE` pour constants
- Type hints obligatoires
- Docstrings pour fonctions publiques
- Max 100 caracteres par ligne
- **Authentification** : utiliser les decorateurs `@require_auth`, `@optional_auth`, `@require_auth_sse` (voir `server/auth.py`) au lieu de verifier manuellement le token dans chaque handler

#### Frontend (TypeScript)
```typescript
// ✅ CORRECT
interface Challenge {
  id: number;
  title: string;
  challengeType: string;
}

export function ChallengeList({ filters }: ChallengeListProps) {
  const { data: challenges, isLoading } = useChallenges(filters);
  
  if (isLoading) return <Skeleton />;
  
  return (
    <div className="grid gap-4">
      {challenges?.map((challenge) => (
        <ChallengeCard key={challenge.id} challenge={challenge} />
      ))}
    </div>
  );
}

// ❌ INCORRECT
export function challengeList(props: any) {
  const challenges = useChallenges(props.filters);
  return <div>{challenges.map(c => <div>{c.title}</div>)}</div>;
}
```

**Règles** :
- `camelCase` pour variables/functions
- `PascalCase` pour composants/interfaces
- Types stricts (pas `any`)
- Composants fonctionnels
- Props interfaces définies

### Tests

**Obligatoire pour** :
- Nouvelles features
- Corrections bugs
- Refactoring logique métier

**Recommandé** :
- Coverage 80%+ pour nouveaux fichiers
- Tests unitaires + intégration
- Tests critiques marqués `@pytest.mark.critical`

```python
# Backend
@pytest.mark.critical
def test_create_challenge(db):
    """Test création challenge"""
    # Arrange
    data = ChallengeCreate(title="Test", ...)
    
    # Act
    result = create_challenge(db, data)
    
    # Assert
    assert result.id is not None
    assert result.title == "Test"
```

```typescript
// Frontend
describe('ChallengeList', () => {
  it('renders challenges', () => {
    render(<ChallengeList />);
    expect(screen.getByText('Challenges')).toBeInTheDocument();
  });
});
```

### Documentation

**Mettre à jour** :
- README si changement installation/usage
- API docs si nouvelles routes
- Architecture docs si changements structurels
- CHANGELOG.md (voir § Versioning)

### Versioning et Changelog

**Convention alpha** : `MAJOR.MINOR.PATCH-alpha.N` (ex. `2.2.0-alpha.1`).

**Checklist avant chaque commit/push significatif** :

| Étape | Fichier | Action |
|-------|---------|--------|
| 1 | `frontend/package.json` | Incrémenter `version` (ex. `alpha.1` → `alpha.2`) |
| 2 | `CHANGELOG.md` | Ajouter section `[X.Y.Z-alpha.N] - date` avec Added/Fixed/Changed |
| 3 | `frontend/messages/fr.json` | Ajouter `changelog.vXXX` (version, date, items[]) |
| 4 | `frontend/messages/en.json` | Idem `changelog.vXXX` |
| 5 | `frontend/app/changelog/page.tsx` | Mettre à jour `versionKeys` si nouvelle version en tête |

**Règle** : la page `/changelog` est orientée utilisateurs — langage simple, pas de jargon technique.

**Exemple** : « Vous pouvez filtrer le classement par âge » ✓ — « Filtre `age_group` sur GET /api/users/leaderboard » ✗

---

## 🔍 CODE REVIEW

### Reviewer Guidelines

**Vérifier** :
- [ ] Code suit conventions
- [ ] Tests passent (CI/CD)
- [ ] Documentation à jour
- [ ] Pas de régression
- [ ] Performance OK
- [ ] Sécurité

**Feedback** :
- 🟢 Approuver si tout OK
- 🟡 Demander changements si nécessaire
- 🔴 Bloquer si problèmes critiques

### Contributor Guidelines

**Répondre aux reviews** :
- Appliquer feedback rapidement
- Expliquer décisions si désaccord
- Tester après modifications

---

## 📚 RESSOURCES

- [Development Guide](DEVELOPMENT.md)
- [Testing Guide](TESTING.md)
- [Architecture](../00-REFERENCE/ARCHITECTURE.md)
- [API Reference](../00-REFERENCE/API.md)

---

## 🎉 REMERCIEMENTS

Merci à tous les contributeurs ! 💙

**Top contributors** :
- @contributor1
- @contributor2
- @contributor3

---

**Questions ?** Ouvrez une [Discussion](https://github.com/yourusername/mathakine/discussions) !

