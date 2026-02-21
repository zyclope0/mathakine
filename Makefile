# Makefile Mathakine - Commandes de développement
# Utilisation: make test-backend-local (Linux/Mac/Git Bash/WSL)

.PHONY: test-backend-local help

help:
	@echo "Commandes disponibles:"
	@echo "  make test-backend-local  Démarre PostgreSQL, init DB, lance pytest"
	@echo "  make help                 Affiche cette aide"

test-backend-local:
	@echo "Lancement des tests backend (PostgreSQL + init + pytest)..."
	python scripts/test_backend_local.py
