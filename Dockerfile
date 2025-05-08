FROM python:3.13-slim

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installation des dépendances spécifiques à Python 3.13
RUN pip install --no-cache-dir sqlalchemy>=2.0.27 fastapi>=0.100.0 pydantic>=2.0.0 pydantic-settings

# Copier le reste des fichiers du projet
COPY . .

# Exposer le port utilisé par l'application
EXPOSE 8081

# Définir les variables d'environnement pour la production
ENV MATH_TRAINER_DEBUG=false
ENV MATH_TRAINER_PROFILE=prod
ENV MATH_TRAINER_PORT=8081

# Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"] 