#!/usr/bin/env python
"""
Script pour générer un rapport sur l'état actuel du projet Mathakine.
Utilise les informations du code source, des fichiers de documentation et du système Git
pour produire un rapport de contexte à jour.
"""

import os
import sys
import subprocess
import datetime
import re
import json
from pathlib import Path

# Définition des chemins
ROOT_DIR = Path(__file__).parent.parent
DOCS_DIR = ROOT_DIR / "docs"
APP_DIR = ROOT_DIR / "app"
CONTEXT_FILE = DOCS_DIR / "CONTEXT.md"
README_FILE = ROOT_DIR / "README.md"



def run_command(command):
    """Exécuter une commande shell et retourner la sortie"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande: {command}")
        print(f"Message d'erreur: {e.stderr}")
        return ""



def get_recent_git_commits(days=30, max_count=10):
    """Obtenir les derniers commits git"""
    command = f'git log --pretty=format:"%h - %s (%cr)" --since="{days} days ago" --max-count={max_count}'
    return run_command(command).split('\n')



def find_api_endpoints():
    """Trouver les endpoints API définis dans le code"""
    endpoints = []
    api_dir = APP_DIR / "api" / "endpoints"

    if not api_dir.exists():
        return endpoints

    for file in api_dir.glob("*.py"):
        content = file.read_text(encoding="utf-8")
        # Chercher les lignes avec @router.get, @router.post, etc.
        matches = re.findall(r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
            , content)
        for method, path in matches:
            endpoints.append(f"{method.upper()} {path}")

    return endpoints



def count_models():
    """Compter les modèles de données définis"""
    models = []
    models_dir = APP_DIR / "models"

    if not models_dir.exists():
        return models

    for file in models_dir.glob("*.py"):
        content = file.read_text(encoding="utf-8")
        # Chercher les classes qui étendent Base (modèles SQLAlchemy)
        matches = re.findall(r'class\s+(\w+)\s*\([^)]*Base[^)]*\):', content)
        models.extend(matches)

    return models



def get_recent_updates():
    """Extraire les mises à jour récentes du fichier RECENT_UPDATES.md"""
    updates_file = DOCS_DIR / "RECENT_UPDATES.md"
    if not updates_file.exists():
        updates_file = DOCS_DIR / "CHANGELOG.md"  # Utiliser CHANGELOG si RECENT_UPDATES n'existe pas
        if not updates_file.exists():
            return []

    content = updates_file.read_text(encoding="utf-8")

    # Adapter le pattern selon le fichier utilisé
    if "CHANGELOG.md" in str(updates_file):
        # Format CHANGELOG.md
        matches = re.findall(r'## \[\d+\.\d+\.\d+\] - ([^\n]+)\n+(?:### ([^\n]+)[\s\S]+?(?=### |## |\[\d+|\Z))+'
            , content)

        updates = []
        for date_str, _ in matches:
            version_section = re.search(rf'## \[\d+\.\d+\.\d+\] - {date_str}([\s\S]+?)(?=## |\Z)'
                , content)
            if version_section:
                sections = re.findall(r'### ([^\n]+)([\s\S]+?)(?=### |## |\Z)', version_section.group(1))
                for category, items_section in sections:
                    items = re.findall(r'- [✅🔄🐛] ([^\n]+)', items_section)
                    if items:
                        updates.append((f"{category} ({date_str})", items))
    else:
        # Format RECENT_UPDATES.md
        matches = re.findall(r'#### ([^\n]+)([\s\S]+?)(?=#### |## |\Z)', content)

        updates = []
        for category, section in matches:
            items = re.findall(r'- \*\*([^*]+)\*\*', section)
            if items:
                date_match = re.search(r'## Dernière mise à jour : ([^\n]+)', content)
                date_str = date_match.group(1) if date_match else "Date inconnue"
                updates.append((f"{category} ({date_str})", items))

    return updates



def get_database_info():
    """Obtenir des informations sur la configuration de la base de données"""
    db_info = {}

    # Chercher le fichier de configuration de la base de données
    db_file = APP_DIR / "db" / "base.py"
    if db_file.exists():
        content = db_file.read_text(encoding="utf-8")
        # Chercher la chaîne de connexion à la base de données
        match = re.search(r'SQLALCHEMY_DATABASE_URL\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            db_info["url"] = match.group(1)

    # Extraire des informations de l'environnement
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        content = env_file.read_text(encoding="utf-8")
        postgres_match = re.search(r'POSTGRES_DB\s*=\s*([^\r\n]+)', content)
        if postgres_match:
            db_info["postgres_db"] = postgres_match.group(1)
            db_info["type"] = "PostgreSQL"

        if "type" not in db_info and "sqlite" in content:
            db_info["type"] = "SQLite"

    return db_info



def get_dependencies():
    """Extraire les principales dépendances du projet"""
    req_file = ROOT_DIR / "requirements.txt"
    if not req_file.exists():
        return []

    dependencies = []
    content = req_file.read_text(encoding="utf-8")

    # Extraire les dépendances principales
    important_deps = ["fastapi", "sqlalchemy", "pydantic", "pytest", "jinja2", "uvicorn"\
        , "psycopg2"]
    for dep in important_deps:
        match = re.search(fr'{dep}[=~<>]=*([0-9.]+)', content)
        if match:
            dependencies.append(f"{dep}=={match.group(1)}")

    return dependencies



def find_important_files():
    """Identifier les fichiers importants du projet"""
    important_files = {
        "Serveur principal": "",
        "CLI": "",
        "Fichiers de configuration": [],
        "Modèles de données principaux": [],
        "Templates principaux": []
    }

    # Rechercher le serveur principal
    for file in ROOT_DIR.glob("*.py"):
        content = file.read_text(encoding="utf-8")
        if "app = FastAPI(" in content or "fastapi import FastAPI" in content:
            important_files["Serveur principal"] = str(file.relative_to(ROOT_DIR))
            break

    # Rechercher le CLI
    for file in ROOT_DIR.glob("*cli*.py"):
        important_files["CLI"] = str(file.relative_to(ROOT_DIR))
        break

    # Fichiers de configuration
    for file in ROOT_DIR.glob("*.env*"):
        if not file.name.endswith(".env.bak"):
            important_files["Fichiers de configuration"].append(str(file.relative_to(ROOT_DIR)))

    # Modèles de données principaux
    models_dir = APP_DIR / "models"
    if models_dir.exists():
        for file in models_dir.glob("*.py"):
            if not file.name == "__init__.py":
                important_files["Modèles de données principaux"].append(f"app/models/{file.name}")

    # Templates principaux
    templates_dir = ROOT_DIR / "templates"
    if templates_dir.exists():
        for file in templates_dir.glob("*.html"):
            if "layout" in file.name or "base" in file.name or "index" in file.name:
                important_files["Templates principaux"].append(f"templates/{file.name}")

    return important_files



def get_test_coverage():
    """Extraire les informations de couverture de test"""
    coverage_info = {"total": "Inconnue", "par_module": {}}

    # Exécuter pytest avec coverage si disponible
    try:
        coverage_output = run_command("pytest --cov=app --cov-report=term-missing")
        total_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', coverage_output)
        if total_match:
            coverage_info["total"] = f"{total_match.group(1)}%"

        # Extraire la couverture par module
        module_matches = re.findall(r'(app/[^\s]+)\s+\d+\s+\d+\s+(\d+)%', coverage_output)
        for module, coverage in module_matches:
            coverage_info["par_module"][module] = f"{coverage}%"
    except:
        # Si pytest-cov n'est pas installé ou échoue, utiliser une autre méthode
        if os.path.exists(ROOT_DIR / ".coverage"):
            coverage_info["total"] = "Le fichier .coverage existe, exécutez 'coverage report' pour voir les détails"

    return coverage_info



def extract_project_status():
    """Extraire des informations sur l'état du projet depuis PROJECT_STATUS.md"""
    status_file = DOCS_DIR / "PROJECT_STATUS.md"
    if not status_file.exists():
        return {}

    content = status_file.read_text(encoding="utf-8")

    status_info = {}

    # Extraire l'itération en cours
    current_iteration = re.search(r'## ITÉRATION EN COURS\s+### (Itération \d+: [^\n]+)', content)
    if current_iteration:
        status_info["iteration_actuelle"] = current_iteration.group(1)

    # Extraire l'état de l'itération
    iteration_state = re.search(r'#### État de l\'Itération\s+[^*]*\*\*([^*]+)\*\*', content)
    if iteration_state:
        status_info["etat_iteration"] = iteration_state.group(1)

    # Extraire les fonctionnalités terminées et en cours
    completed_tasks = re.findall(r'- \[x\] ([^\n]+)', content)
    pending_tasks = re.findall(r'- \[ \] ([^\n]+)', content)

    status_info["fonctionnalites_terminees"] = completed_tasks[:5]  # Les 5 plus récentes
    status_info["fonctionnalites_en_cours"] = pending_tasks[:3]     # Les 3 prochaines

    return status_info



def identify_issues():
    """Identifier les problèmes connus ou défis actuels"""
    issues = []

    # Rechercher dans le fichier TROUBLESHOOTING.md
    troubleshooting_file = DOCS_DIR / "TROUBLESHOOTING.md"
    if troubleshooting_file.exists():
        content = troubleshooting_file.read_text(encoding="utf-8")
        # Trouver les problèmes communs
        matches = re.findall(r'## (Problème:[^\n]+)', content)
        issues.extend(matches[:3])  # Prendre les 3 premiers problèmes

    # Rechercher les TODOs et FIXMEs dans le code
    todos = []
    for ext in [".py", ".md", ".html", ".js"]:
        for file in ROOT_DIR.glob(f"**/*{ext}"):
            if "venv" in str(file) or ".git" in str(file):
                continue

            try:
                content = file.read_text(encoding="utf-8")
                # Trouver les TODOs et FIXMEs
                todo_matches = re.findall(r'(TODO|FIXME):\s*([^\n]+)', content)
                for typ, msg in todo_matches:
                    todos.append(f"{typ}: {msg.strip()} ({file.relative_to(ROOT_DIR)})")
            except:
                continue

    issues.extend(todos[:5])  # Ajouter les 5 premiers TODOs/FIXMEs

    return issues



def generate_context_report():
    """Générer le rapport de contexte complet"""
    now = datetime.datetime.now()
    date_str = now.strftime("%d/%m/%Y")

    # Récupérer les informations
    recent_commits = get_recent_git_commits()
    api_endpoints = find_api_endpoints()
    models = count_models()
    recent_updates = get_recent_updates()
    db_info = get_database_info()
    dependencies = get_dependencies()
    important_files = find_important_files()
    test_coverage = get_test_coverage()
    project_status = extract_project_status()
    issues = identify_issues()

    # Construire le rapport
    report = [
        "# Rapport sur l'état actuel du projet Mathakine",
        f"\nGénéré automatiquement le {date_str}\n",
        "## Activité récente du code",
    ]

    if recent_commits:
        report.append("\n### Derniers commits")
        for commit in recent_commits:
            if commit:  # Éviter les lignes vides
                report.append(f"- {commit}")

    report.append("\n## Structure de l'application")

    if models:
        report.append(f"\n### Modèles de données ({len(models)})")
        for model in models:
            report.append(f"- {model}")

    if api_endpoints:
        report.append(f"\n### API Endpoints ({len(api_endpoints)})")
        for endpoint in sorted(api_endpoints):
            report.append(f"- {endpoint}")

    # Ajouter les fichiers importants
    report.append("\n### Fichiers importants")
    for category, files in important_files.items():
        if isinstance(files, str) and files:
            report.append(f"- **{category}**: {files}")
        elif isinstance(files, list) and files:
            report.append(f"- **{category}**:")
            for file in files:
                report.append(f"  - {file}")

    # Ajouter les dépendances
    if dependencies:
        report.append("\n### Dépendances principales")
        for dep in dependencies:
            report.append(f"- {dep}")

    # Information sur l'état du projet
    if project_status:
        report.append("\n## État du projet")

        if "iteration_actuelle" in project_status:
            report.append(f"\n### {project_status['iteration_actuelle']}")

        if "etat_iteration" in project_status:
            report.append(f"\nÉtat: **{project_status['etat_iteration']}**")

        if "fonctionnalites_terminees" in project_status and project_status['fonctionnalites_terminees']:
            report.append("\n#### Fonctionnalités récemment terminées")
            for task in project_status['fonctionnalites_terminees']:
                report.append(f"- ✅ {task}")

        if "fonctionnalites_en_cours" in project_status and project_status['fonctionnalites_en_cours']:
            report.append("\n#### Prochaines fonctionnalités prévues")
            for task in project_status['fonctionnalites_en_cours']:
                report.append(f"- 🔄 {task}")

    # Information sur la couverture de test
    report.append("\n## Tests et qualité du code")
    report.append(f"\n- **Couverture de test**: {test_coverage['total']}")

    # Problèmes connus
    if issues:
        report.append("\n### Problèmes connus et TODOs")
        for issue in issues:
            report.append(f"- {issue}")

    if recent_updates:
        report.append("\n## Mises à jour récentes")
        for category, items in recent_updates:
            report.append(f"\n### {category}")
            for item in items[:5]:  # Limiter à 5 éléments par section
                report.append(f"- {item}")

    if db_info:
        report.append("\n## Configuration de la base de données")
        for key, value in db_info.items():
            if key == "type":
                report.append(f"- **Type**: {value}")
            elif key == "postgres_db" and value:
                report.append(f"- **Nom de la base PostgreSQL**: {value}")
            elif key == "url" and not any(sensitive in value for sensitive in ["password"
                , "passwd", "pwd"]):
                # Éviter d'afficher les URL avec mots de passe
                report.append(f"- **URL de connexion**: {value}")

    report.append("\n## Actions recommandées")
    report.append("\n1. Mettre à jour le fichier `docs/CONTEXT.md` avec ces informations")
    report.append("2. Vérifier les derniers commits pour comprendre les changements récents")
    report.append("3. Examiner les endpoints API pour comprendre la structure actuelle")
    if issues:
        report.append("4. Résoudre les problèmes identifiés")

    report.append("\n---\n")
    report.append("*Ce rapport est généré automatiquement pour aider à maintenir le contexte du projet.*")

    return "\n".join(report)



def update_context_file(report):
    """Mettre à jour le fichier CONTEXT.md avec le rapport généré"""
    if not CONTEXT_FILE.exists():
        # Créer un nouveau fichier CONTEXT.md
        header = "# Contexte du projet Mathakine\n\n"
        description = "Ce document sert de point d'entrée rapide pour comprendre l'état actuel du projet\
            , son historique récent et les principales ressources. Il est conçu pour fournir un contexte immédiat.\n\n"
        last_update = f"*Dernière mise à jour: {datetime.datetime.now().strftime('%d/%m/%Y')}*\n\n"

        # Extraire la section "Rapport sur l'état actuel" du rapport
        state_report = report.split("## Structure de l'application")[0]

        # Contenu final
        content = header + description + state_report

        # Ajouter des sections statiques au besoin
        architecture_section = """## Architecture technique

### Stack technologique
- **Backend**: FastAPI (Python)
- **Base de données**: PostgreSQL (production), SQLite (développement)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic v2
- **Frontend**: Templates HTML avec JavaScript
- **Déploiement**: Render

### Structure simplifiée
```
app/                # Code principal de l'application
├── api/            # Endpoints API
├── models/         # Modèles de données SQLAlchemy
├── schemas/        # Schémas Pydantic
├── core/           # Configuration centrale
└── db/             # Gestion de base de données

templates/          # Templates HTML frontend
static/             # Ressources statiques (CSS, JS, images)
tests/              # Tests (unitaires, API, intégration, fonctionnels)
scripts/            # Scripts utilitaires
docs/               # Documentation
```

"""

        resources_section = """## Points d'entrée importants

### Documentation essentielle
- **Vue d'ensemble**: [README.md](../README.md)
- **Mises à jour récentes**: [docs/CHANGELOG.md](CHANGELOG.md)
- **Résolution de problèmes**: [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Guide de démarrage**: [GETTING_STARTED.md](../GETTING_STARTED.md)

### Fichiers clés
- **Point d'entrée principal**: `app/main.py`
- **Endpoints exercices**: `app/api/endpoints/exercises.py`
- **Modèle exercices**: `app/models/exercise.py`
- **Frontend exercices**: `templates/exercises.html`

"""

        maintenance_section = """## Comment maintenir le contexte dans le futur

1. **Mettre à jour ce fichier** - Actualiser ce document après chaque changement significatif
2. **Consulter les logs git** - Utiliser `git log --oneline --since="2 weeks ago"` pour voir les changements récents
3. **Vérifier l'état des tickets** - Examiner périodiquement les issues GitHub
4. **Utiliser les tags git** - Consulter les tags pour voir les versions stables

"""

        final_content = (
            header +
            description +
            last_update +
            state_report +
            architecture_section +
            resources_section +
            maintenance_section
        )

        CONTEXT_FILE.write_text(final_content, encoding="utf-8")
        return True
    else:
        # Mettre à jour le fichier existant
        existing_content = CONTEXT_FILE.read_text(encoding="utf-8")

        # Extraire la section "Rapport sur l'état actuel" du rapport
        state_report_match = re.search(r'# Rapport sur l\'état actuel du projet Mathakine([\s\S]+?)(?=\n## Structure de l\'application|\Z)'
            , report)
        if state_report_match:
            state_report = state_report_match.group(1)

            # Remplacer la section "État actuel" dans le fichier existant
            updated_content = re.sub(
                r'## État actuel[\s\S]+?(?=\n## Architecture technique|\n## Points d\'entrée|\Z)',
                f"## État actuel{state_report}",
                existing_content
            )

            # Mettre à jour la date de dernière mise à jour
            updated_content = re.sub(
                r'\*Dernière mise à jour: .*?\*',
                f'*Dernière mise à jour: {datetime.datetime.now().strftime("%d/%m/%Y")}*',
                updated_content
            )

            # Écrire le contenu mis à jour
            CONTEXT_FILE.write_text(updated_content, encoding="utf-8")
            return True

    return False



def print_usage():
    """Afficher l'aide d'utilisation"""
    print(f"Usage: {sys.argv[0]} [options]")
    print("Options:")
    print("  --update   Met à jour directement le fichier CONTEXT.md avec les informations générées")
    print("  --json     Génère le rapport au format JSON")
    print("  --help     Affiche cette aide")



def main():
    """Fonction principale"""
    # Analyser les arguments
    update_context = "--update" in sys.argv
    json_output = "--json" in sys.argv
    show_help = "--help" in sys.argv

    if show_help:
        print_usage()
        return

    # Générer le rapport
    report = generate_context_report()

    if json_output:
        # Convertir le rapport en JSON
        # Ceci est une conversion simplifiée, une version plus élaborée
        # pourrait parser le rapport en sections structurées
        sections = {}
        current_section = "general"

        for line in report.split("\n"):
            if line.startswith("## "):
                current_section = line[3:].strip().lower().replace(" ", "_")
                sections[current_section] = []
            elif line.startswith("### "):
                subsection = line[4:].strip()
                sections[current_section].append({"subsection": subsection, "items": []})
            elif line.startswith("- "):
                item = line[2:].strip()
                if sections[current_section] and isinstance(sections[current_section][-1], dict):
                    sections[current_section][-1]["items"].append(item)
                else:
                    sections[current_section].append(item)

        print(json.dumps(sections, indent=2))
    elif update_context:
        # Mettre à jour le fichier CONTEXT.md
        success = update_context_file(report)
        if success:
            print(f"Le fichier {CONTEXT_FILE} a été mis à jour avec succès.")
        else:
            print(f"Erreur lors de la mise à jour du fichier {CONTEXT_FILE}.")
    else:
        # Afficher le rapport sur la sortie standard
        print(report)

if __name__ == "__main__":
    main()
