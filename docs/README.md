# Documentation Mathakine

Ce dossier contient toute la documentation du projet Mathakine (anciennement Math Trainer), une application éducative pour l'apprentissage des mathématiques et de la logique avec une thématique Star Wars.

## Organisation de la documentation

La documentation est organisée par thématiques :

- **Démarrage** : Installation, configuration, déploiement
- **Architecture** : Structure du code, modèles de données, API
- **Fonctionnalités** : Documentation détaillée des fonctionnalités
- **Maintenance** : Guides pour la maintenance et le nettoyage
- **Historique** : Changements, refactorings, migrations

## Comment naviguer dans la documentation

1. Commencez par consulter la [Table des matières](TABLE_DES_MATIERES.md) qui offre une vue d'ensemble organisée.
2. Pour les nouveaux contributeurs, le [Guide du développeur](GUIDE_DEVELOPPEUR.md) est le meilleur point de départ.
3. Pour comprendre le modèle de données, consultez [Schéma de la base de données](SCHEMA.md).
4. Pour les API, consultez la [Référence API](API_REFERENCE.md).

## Mises à jour récentes (Mai 2025)

Deux améliorations majeures ont été récemment documentées :

1. **Gestion unifiée des suppressions en cascade** ([CASCADE_DELETION.md](CASCADE_DELETION.md))
   - Implémentation des relations avec `cascade="all, delete-orphan"`
   - Standardisation des endpoints de suppression
   - Documentation des bonnes pratiques

2. **Sécurité des migrations Alembic** ([ALEMBIC_SÉCURITÉ.md](ALEMBIC_SÉCURITÉ.md))
   - Nouveaux scripts de sauvegarde et restauration
   - Procédures sécurisées pour les migrations en production
   - Détection des opérations dangereuses

La documentation de l'API a également été mise à jour avec les nouveaux endpoints de suppression dans [API_REFERENCE.md](API_REFERENCE.md).

## Contributions à la documentation

Pour contribuer à la documentation :

1. Assurez-vous que la documentation suit le format Markdown standard
2. Placez les nouveaux documents dans le dossier approprié
3. Mettez à jour la [Table des matières](TABLE_DES_MATIERES.md)
4. Maintenez la cohérence du style et de la terminologie
5. Utilisez des emojis pour améliorer la lisibilité des titres (📝, 🚀, etc.)

## Documentation obsolète

La documentation obsolète est déplacée dans le dossier [ARCHIVE](ARCHIVE/) plutôt que d'être supprimée, afin de conserver l'historique.

---

*Pour toute question sur la documentation, contactez l'équipe de développement Mathakine.* 