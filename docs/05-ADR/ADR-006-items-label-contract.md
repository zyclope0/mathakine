# ADR-006 : Contrat d'affichage unifié des éléments de `visual_data`

**Date :** 2026-04-22
**Statut :** Accepté

---

## Contexte

Les défis logiques consomment des `visual_data` hétérogènes produits par un LLM
et parfois persistés depuis plusieurs générations successives. Chaque type de
défi a ses propres arrays d'« éléments » pédagogiques :

- `visual.layout[].shape` (symétrie) ;
- `puzzle.pieces[]` ;
- `sequence.items[]` ;
- `pattern.grid[]` ;
- `graph.nodes[]` / `graph.edges[]` ;
- `riddle.clues[]`, `riddle.hints[]`, `riddle.pots[]` ;
- `deduction.entities`, `deduction.attributes` ;
- `probability.urns[]` ;
- `coding.examples[]` ;
- `chess.moves[]`.

Le même élément peut arriver sous **trois formes** selon le modèle / la
prompt / l'ancienneté de la génération :

1. Chaîne plate : `"cercle rouge"`, `"Alice"`, `"P1"`.
2. Objet riche : `{ "label": "Alice" }`, `{ "name": "cercle", "size": "petit" }`,
   `{ "id": "P1", "left": "3", "right": "5" }`.
3. Chaîne héritée « repr Python » : `"{'name': 'cercle rouge', 'size': 'petit'}"`
   ou `'{"id":"P1","left":"3","right":"5"}'` — produites par d'anciens
   `str(dict)` / `JSON.stringify(dict)` côté backend.

Chaque renderer et chaque validateur avait sa propre logique ad hoc pour
extraire un libellé affichable. À chaque nouveau contrat LLM (par exemple
`{ id, pattern }` pour puzzle, `{ token, ... }` pour sequence), le défaut
silencieux apparaissait dans au moins un composant :

- Backend : `str(dict)` → ligne `{'id': 'A', ...}` persistée en DB.
- Frontend : `JSON.stringify(item)` / `String(item)` → `{"id":"A",...}` /
  `[object Object]` affiché à l'élève.

Cette classe de bug a été identifiée cinq fois en une semaine (défi n°4070
visual, validation puzzle n°4070-bis, PuzzleRenderer, SequenceRenderer,
RiddleRenderer). Un patch ciblé par cas ne suffit plus : il faut un
**contrat de lecture partagé**.

## Décision

Nous introduisons un **contrat d'affichage unifié** pour tout élément
arbitraire de `visual_data`, avec deux helpers jumeaux :

- **Backend** — `app/services/challenges/challenge_ordering_utils.py::item_label`.
- **Frontend** — `frontend/components/challenges/visualizations/_itemLabel.ts::itemLabel`.

### Règles

1. **Ordre de lecture officiel** des champs textuels dans un dict :

   ```
   label → value → name → text → description → id → piece_id → tag
   ```

   Ce tuple est exposé comme constante (`DEFAULT_ITEM_LABEL_FIELDS` /
   `DEFAULT_ITEM_LABEL_FIELDS`) des deux côtés, synchronisée par un test
   unitaire dédié.

2. **Types acceptés en entrée** :
   - `string` : `trim()` + reparse opportuniste `parseDictLikeLabel` /
     `_parse_python_dict_like_label_str` pour rattraper les chaînes héritées.
   - `number` (fini) / `int` / `float` : conversion canonique.
   - `dict` / `object` : parcours des champs officiels. Retourne le premier
     texte non vide.
   - `bool`, `list`, `tuple`, `set`, `None`, `NaN` : refus explicite.

3. **Fail-open `""`**. Jamais `str(dict)`, jamais `JSON.stringify(obj)` pour un
   libellé visible. Si aucun champ reconnu, on retourne une chaîne vide ;
   l'appelant choisit un fallback explicite (`"#1"`, `"—"`, etc.).

4. **Override de champs** : chaque renderer peut passer `fields=[...]` pour
   prioriser une clé spécifique au domaine (ex. `RiddleRenderer` privilégie
   `text` avant `label`), sans duplication de la règle globale.

5. **Exception explicite** : `DefaultRenderer` est autorisé à appeler
   `JSON.stringify(visualData, null, 2)` **uniquement** dans son mode "Vue
   JSON" (badge `json`, toggle explicite, `font-mono`). C'est un JSON
   explorer volontaire, pas une interface pédagogique.

### Tests anti-régression obligatoires

Deux familles de tests :

- **Unitaire** :
  `tests/unit/test_challenge_item_label.py` (back) +
  `frontend/.../_itemLabel.test.ts` (front). Ils couvrent la table de vérité
  complète et verrouillent l'ordre des champs officiels (symétrie back↔front).

- **Rendu** : `frontend/.../ItemLabelContract.renderers.test.tsx` monte chaque
  renderer avec des contrats LLM mixtes (objets `{id}`, `{label}`, `{value}`,
  `{name}`, chaînes Python-like) et asserte que le `textContent` ne contient
  jamais :

  ```
  /\{\s*['"]id['"]/   // repr Python ``{'id'`` ou JSON ``{"id"``
  /\[object Object\]/
  ```

  Tout nouveau renderer doit rejoindre ce fichier de test.

## Conséquences

**Positives**

- La classe de bug « repr brute dans l'UI » est fermée de manière
  structurelle : plus de patch ponctuel par renderer.
- Les défis persistés avec des `shape` / `piece` dégradés sont rattrapés à la
  lecture par le reparse, sans migration DB.
- Les prochains contrats LLM exotiques (`{token}`, `{symbol}`, etc.) tombent
  soit sur un champ officiel, soit sur le fallback explicite du renderer,
  jamais sur un `[object Object]` visible.

**Coûts / contraintes**

- Tout nouveau champ-libellé imaginé par le LLM et non couvert par la liste
  officielle doit être traité en amont (normalisation backend) **ou**
  référencé via `fields=[...]` dans le renderer concerné. C'est un coût
  d'ajout, pas un coût récurrent.
- Les checklists de PR côté `frontend/components/challenges/visualizations/`
  doivent intégrer la règle : tout `JSON.stringify(x)` / `String(obj)` en
  position affichable est un défaut, sauf cas `DefaultRenderer` explicite.

## Portée et migration

- **Lot M étape 1** (commit `e30ec63`) : helpers back+front, branchement
  `PuzzleRenderer` / `SequenceRenderer` / `RiddleRenderer`, tests.
- **Lot M étape 2** (ce commit) : branchement `DeductionRenderer` /
  `CodingRenderer` / `ProbabilityRenderer` / `VisualRenderer` (mode
  `rawData`), extension du test anti-régression, cet ADR.
- Les renderers `GraphRenderer` et `ChessRenderer` n'ont pas de chemin
  affichable "objet inconnu → libellé" identifié à ce jour : ils sont
  couverts par la revue continue plutôt qu'un branchement mécanique, et
  peuvent rejoindre `ItemLabelContract.renderers.test.tsx` si un nouveau cas
  apparaît.
- `PatternRenderer` affiche une grille numérique / pictogramme sans étape
  intermédiaire « objet libellé » : pas de branchement nécessaire tant que
  le contrat grille reste primitif. À surveiller si le LLM commence à y
  injecter des objets.

## Références

- Lot M étape 1 (`e30ec63`) : `feat(challenges): unified item-label contract`.
- Lot M étape 2 (ce commit) : 5 renderers additionnels + ADR-006.
- Historique du pattern : bug visual n°4070 (commit `090d8bf`), bug puzzle
  id/piece_label (commit `c936c2d`).
