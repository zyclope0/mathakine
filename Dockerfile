FROM python:3.11-slim

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers du projet
COPY . .

# Exposer le port utilisé par l'application
EXPOSE 8081

# Variable d'environnement pour l'API OpenAI (à remplacer lors du déploiement)
ENV OPENAI_API_KEY=""

# Commande pour démarrer l'application
CMD ["uvicorn", "enhanced_server:app", "--host", "0.0.0.0", "--port", "8081"] 