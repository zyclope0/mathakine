#!/bin/bash
# Helper de démarrage "Render-like" (backend)
# Date: 06/02/2026
# Description: Applique migrations Alembic puis démarre Gunicorn + UvicornWorker

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

# 3. Démarrer le serveur ASGI de production
echo ""
PORT="${PORT:-10000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
echo "🚀 Démarrage Gunicorn/UvicornWorker (port ${PORT}, workers ${WEB_CONCURRENCY})..."
exec gunicorn enhanced_server:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --graceful-timeout 30 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
