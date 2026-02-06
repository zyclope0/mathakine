# 🐳 DOCKER GUIDE - MATHAKINE

**Version** : 2.0.0  
**Date** : 20 novembre 2025  
**Audience** : DevOps, Développeurs

---

## 🎯 VUE D'ENSEMBLE

Docker permet de conteneuriser Mathakine pour un déploiement uniforme sur tous les environnements.

### Services
- **Backend** : Python 3.11 + Starlette
- **Frontend** : Node.js 20 + Next.js
- **Database** : PostgreSQL 15

---

## 📦 DOCKERFILES

### Backend Dockerfile

```dockerfile
# Dockerfile (racine projet)
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="mathakine@example.com"
LABEL version="2.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Répertoire de travail
WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .

# Installer dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier code
COPY app/ ./app/
COPY server/ ./server/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY enhanced_server.py .

# Créer utilisateur non-root
RUN useradd -m -u 1000 mathakine && \
    chown -R mathakine:mathakine /app

USER mathakine

# Port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Commande
CMD ["python", "enhanced_server.py"]
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base

# Dependencies
FROM base AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# Builder
FROM base AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Variables d'environnement build
ENV NEXT_TELEMETRY_DISABLED=1
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# Build
RUN npm run build

# Runner
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Créer utilisateur non-root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copier fichiers nécessaires
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

---

## 🐳 DOCKER COMPOSE

### Development (docker-compose.yml)

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: mathakine-db
    environment:
      POSTGRES_USER: mathakine_user
      POSTGRES_PASSWORD: mathakine_password
      POSTGRES_DB: mathakine_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mathakine_user"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mathakine-backend
    environment:
      DATABASE_URL: postgresql://mathakine_user:mathakine_password@db:5432/mathakine_db
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_ORIGINS: http://localhost:3000
      DEBUG: "True"
      LOG_LEVEL: DEBUG
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app
      - ./server:/app/server
    depends_on:
      db:
        condition: service_healthy
    command: python enhanced_server.py
  
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_BASE_URL: http://localhost:8000
    container_name: mathakine-frontend
    environment:
      NEXT_PUBLIC_API_BASE_URL: http://backend:8000
      NEXT_PUBLIC_API_URL: http://backend:8000/api
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Production (docker-compose.prod.yml)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - mathakine-network
  
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
      DEBUG: "False"
      LOG_LEVEL: INFO
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
    networks:
      - mathakine-network
  
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_BASE_URL: ${API_BASE_URL}
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_BASE_URL: ${API_BASE_URL}
      NEXT_PUBLIC_API_URL: ${API_BASE_URL}/api
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - mathakine-network

volumes:
  postgres_data:

networks:
  mathakine-network:
    driver: bridge
```

---

## 🚀 UTILISATION

### Development

```bash
# Démarrer tous les services
docker-compose up

# En arrière-plan
docker-compose up -d

# Voir logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend

# Arrêter
docker-compose down

# Arrêter et supprimer volumes
docker-compose down -v
```

### Production

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Démarrer
docker-compose -f docker-compose.prod.yml up -d

# Voir statut
docker-compose -f docker-compose.prod.yml ps

# Logs
docker-compose -f docker-compose.prod.yml logs -f

# Arrêter
docker-compose -f docker-compose.prod.yml down
```

### Commandes utiles

```bash
# Entrer dans container
docker-compose exec backend bash
docker-compose exec frontend sh

# Lancer migrations
docker-compose exec backend alembic upgrade head

# Tests
docker-compose exec backend pytest tests/ -v

# Rebuild un service
docker-compose build backend
docker-compose up -d backend

# Voir volumes
docker volume ls

# Nettoyer images non utilisées
docker image prune -a
```

---

## 📊 ENVIRONNEMENT

### .env (Development)

```bash
# .env
SECRET_KEY=dev-secret-key-not-for-production
POSTGRES_USER=mathakine_user
POSTGRES_PASSWORD=mathakine_password
POSTGRES_DB=mathakine_db
ALLOWED_ORIGINS=http://localhost:3000
API_BASE_URL=http://localhost:8000
OPENAI_API_KEY=sk-...
```

### .env.production (Production)

```bash
# .env.production
SECRET_KEY=<generate-secure-key>
POSTGRES_USER=mathakine_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=mathakine_prod
ALLOWED_ORIGINS=https://mathakine.com
API_BASE_URL=https://api.mathakine.com
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG...
```

---

## 🔧 TROUBLESHOOTING

### Backend ne démarre pas

```bash
# Voir logs détaillés
docker-compose logs backend

# Vérifier variables d'environnement
docker-compose exec backend env

# Tester connexion DB
docker-compose exec backend python -c "from app.db.base import engine; engine.connect()"
```

### Database connection failed

```bash
# Vérifier DB actif
docker-compose ps db

# Voir logs DB
docker-compose logs db

# Tester depuis backend
docker-compose exec backend pg_isready -h db -U mathakine_user
```

### Port déjà utilisé

```bash
# Changer port dans docker-compose.yml
services:
  backend:
    ports:
      - "8001:8000"  # Host:Container
```

---

## 📚 RESSOURCES

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Deployment Guide](DEPLOYMENT.md)

---

**Bon containerizing !** 🐳🚀

