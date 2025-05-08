### Migration vers PostgreSQL

Pour migrer de SQLite vers PostgreSQL (recommandé pour la production) :

1. Assurez-vous que PostgreSQL est installé et en cours d'exécution
2. Configurez les variables d'environnement dans le fichier `.env` :
   ```
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=votre_mot_de_passe
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=mathakine
   ```
3. Exécutez le script de migration :
   ```bash
   scripts/migrate_to_postgres.bat
   ```

Le script va :
- Créer la base de données PostgreSQL si elle n'existe pas
- Créer toutes les tables avec la même structure que SQLite
- Migrer toutes les données existantes
- Afficher un rapport détaillé de la migration 