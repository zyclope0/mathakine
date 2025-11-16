#!/bin/bash
# Script de vérification TypeScript avant déploiement
# Usage: ./scripts/check_types_before_deploy.sh

set -e

echo "🔍 Vérification TypeScript complète avant déploiement..."
echo ""

cd frontend

echo "📦 Installation des dépendances..."
npm install --silent

echo ""
echo "🔨 Build TypeScript..."
if npm run build; then
    echo ""
    echo "✅ Build réussi ! Aucune erreur TypeScript détectée."
    exit 0
else
    echo ""
    echo "❌ Build échoué ! Des erreurs TypeScript ont été détectées."
    echo "Corrigez les erreurs avant de déployer."
    exit 1
fi

