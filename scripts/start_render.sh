#!/bin/bash
# Script de démarrage Render (Mathakine Backend)
# Date: 06/02/2026
# Description: Applique migrations Alembic puis démarre serveur Starlette

set -e  # Arrêter si erreur

echo "=== Mathakine Backend - Démarrage Render ==="
echo "Date: $(date)"
echo "Révision: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
echo ""

# 1. Appliquer migrations Alembic
echo "📊 Application des migrations Alembic..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations appliquées avec succès"
else
    echo "❌ ERREUR lors des migrations"
    exit 1
fi

# 2. Afficher révision actuelle
echo ""
echo "📌 Révision DB actuelle:"
alembic current

# 3. Démarrer le serveur Starlette
echo ""
echo "🚀 Démarrage du serveur Starlette (port 10000)..."
exec python enhanced_server.py
