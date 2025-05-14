# Archives de la Documentation

Ce dossier contient les documents archivés du projet Mathakine, organisés par année.

## Structure

```
ARCHIVE/
├── 2024/          # Documents de 2024
│   ├── PYDANTIC_V2_MIGRATION.md
│   ├── LOGGING.md
│   ├── POSTGRESQL_MIGRATION.md
│   ├── CLEANUP_REPORT.md
│   └── HISTORIQUE_REFACTORING.md
│
└── 2025/          # Documents de 2025
    ├── IMPLEMENTATION_PLAN_DOCUMENTATION.md
    ├── DOCUMENT_CONVERSION_STATUS.md
    └── ...
```

## Politique d'archivage

1. Les documents sont archivés par année de dernière modification
2. Les documents consolidés dans la nouvelle structure sont archivés pour référence historique
3. Les redirections (.redirect) sont supprimées car redondantes
4. Les documents d'exemple ou temporaires sont supprimés

## Accès aux archives

Pour accéder à un document archivé :
1. Naviguez vers le dossier de l'année appropriée
2. Le document conserve son nom d'origine
3. Les liens dans les documents archivés peuvent être obsolètes

## Script d'archivage

Un script Python (`scripts/archive_docs.py`) est disponible pour gérer l'archivage automatique des documents. Pour l'utiliser :

```bash
python scripts/archive_docs.py
```

## Notes importantes

- Les documents archivés sont en lecture seule
- Pour toute modification, créez une nouvelle version dans la structure actuelle
- Les documents archivés sont conservés pour référence historique uniquement
- La documentation active se trouve dans les dossiers Core/, Tech/ et Features/

---

*Dernière mise à jour : 15 juin 2025* 