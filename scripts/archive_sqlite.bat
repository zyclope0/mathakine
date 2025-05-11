@echo off
echo Archivage des fichiers SQLite...

set ARCHIVE_DIR=archives\sqlite

if not exist %ARCHIVE_DIR% (
    mkdir %ARCHIVE_DIR%
    echo Répertoire d'archives créé: %ARCHIVE_DIR%
)

:: Déplacer les fichiers de base de données SQLite existants
if exist *.db (
    move *.db %ARCHIVE_DIR%\
    echo Fichiers SQLite .db déplacés dans %ARCHIVE_DIR%
)

:: Archiver les scripts SQLite
if exist toggle_database.py (
    copy scripts\toggle_database.py %ARCHIVE_DIR%\
    echo toggle_database.py archivé
)

if exist scripts\migrate_to_sqlite.py (
    copy scripts\migrate_to_sqlite.py %ARCHIVE_DIR%\
    echo migrate_to_sqlite.py archivé
)

:: Mettre à jour les fichiers de configuration
echo Mise à jour du fichier .env pour utiliser uniquement PostgreSQL...

:: Supprimer les références à SQLite dans .env
powershell -Command "(Get-Content .env) | Where-Object { $_ -notmatch 'sqlite' -and $_ -notmatch 'DB_PATH' } | Set-Content .env.tmp"
move /Y .env.tmp .env

echo Archivage terminé.
echo Les fichiers ont été déplacés dans %ARCHIVE_DIR%
echo La configuration a été mise à jour pour utiliser uniquement PostgreSQL. 