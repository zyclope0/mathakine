#!/bin/bash
# Script pour lancer le serveur en mode test avec les bonnes variables d'environnement

echo "========================================"
echo "🚀 DÉMARRAGE SERVEUR EN MODE TEST"
echo "========================================"
echo ""

# Configuration pour les tests
export MATH_TRAINER_DEBUG=true
export MATH_TRAINER_PROFILE=dev
export LOG_LEVEL=DEBUG

# Sécurité - Mode développement (relaxé pour les tests)
export REQUIRE_STRONG_DEFAULT_ADMIN=false
export RUN_STARTUP_MIGRATIONS=true

# Base de données (utiliser la base de test si disponible)
if [ -z "$TEST_DATABASE_URL" ]; then
    echo "⚠️  TEST_DATABASE_URL non défini, utilisation de DATABASE_URL"
else
    echo "✅ Utilisation de TEST_DATABASE_URL pour les tests"
fi

echo ""
echo "Configuration:"
echo "  - DEBUG: $MATH_TRAINER_DEBUG"
echo "  - RUN_STARTUP_MIGRATIONS: $RUN_STARTUP_MIGRATIONS"
echo "  - REQUIRE_STRONG_DEFAULT_ADMIN: $REQUIRE_STRONG_DEFAULT_ADMIN"
echo ""

echo "Démarrage du serveur..."
echo ""

python enhanced_server.py

