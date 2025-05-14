"""
Messages et textes centralisés pour l'application Mathakine
Ce fichier contient tous les messages et textes utilisés dans l'application.
"""

# Messages système
class SystemMessages:
    # Erreurs
    ERROR_DATABASE_CONNECTION = "Erreur de connexion à la base de données"
    ERROR_EXERCISE_NOT_FOUND = "Exercice non trouvé"
    ERROR_INTERNAL_SERVER = "Erreur interne du serveur"
    ERROR_AUTHENTICATION_REQUIRED = "Authentification requise"
    ERROR_PERMISSION_DENIED = "Permission refusée"
    ERROR_INVALID_REQUEST = "Requête invalide"
    ERROR_NOT_IMPLEMENTED = "Fonctionnalité non implémentée"
    ERROR_RESOURCE_NOT_FOUND = "Ressource non trouvée"
    
    # Succès
    SUCCESS_OPERATION_COMPLETED = "Opération réussie"
    SUCCESS_CREATED = "Ressource créée avec succès"
    SUCCESS_UPDATED = "Ressource mise à jour avec succès"
    SUCCESS_DELETED = "Ressource supprimée avec succès"
    SUCCESS_ARCHIVED = "Ressource archivée avec succès"
    
    # Messages d'information
    INFO_TRYING_CONNECTION = "Tentative de connexion à la base de données"
    INFO_APP_STARTING = "Démarrage de l'application"
    INFO_APP_READY = "Application prête"
    INFO_APP_STOPPING = "Arrêt de l'application"

# Messages liés aux exercices
class ExerciseMessages:
    # Titres des exercices
    TITLE_ADDITION = "Addition de nombres"
    TITLE_SUBTRACTION = "Soustraction de nombres"
    TITLE_MULTIPLICATION = "Multiplication de nombres"
    TITLE_DIVISION = "Division de nombres"
    TITLE_FRACTIONS = "Calcul de fractions"
    TITLE_GEOMETRIE = "Exercice de géométrie"
    TITLE_DIVERS = "Exercice divers"
    TITLE_DEFAULT = "Exercice de calcul"
    TITLE_AI_PREFIX = "TEST-ZAXXON"
    
    # Messages de résultats
    RESULT_CORRECT = "Excellent travail ! Ta réponse est correcte."
    RESULT_INCORRECT = "Pas tout à fait ! Essaie encore."
    RESULT_HINT = "Indice: {hint}"
    
    # Questions types
    QUESTION_ADDITION = "Combien font {num1} + {num2}?"
    QUESTION_SUBTRACTION = "Combien font {num1} - {num2}?"
    QUESTION_MULTIPLICATION = "Combien font {num1} × {num2}?"
    QUESTION_DIVISION = "Combien font {num1} ÷ {num2}?"
    QUESTION_FRACTIONS = "Calcule la fraction {num1}/{num2} {operation} {num3}/{num4}"
    QUESTION_GEOMETRIE = "Calcule {property} {shape} avec {parameter1}={value1} et {parameter2}={value2}"
    QUESTION_DIVERS = "Résous ce problème: {problem}"
    
    # Textes éducatifs
    EXPLANATION_ADDITION = "{num1} + {num2} = {result}"
    EXPLANATION_SUBTRACTION = "{num1} - {num2} = {result}"
    EXPLANATION_MULTIPLICATION = "{num1} × {num2} = {result}"
    EXPLANATION_DIVISION = "{num1} ÷ {num2} = {result}"
    EXPLANATION_FRACTIONS = "Pour calculer {num1}/{num2} {operation} {num3}/{num4}, il faut {steps}. Le résultat est {result}."
    EXPLANATION_GEOMETRIE = "Pour calculer {property} {shape}, on utilise la formule {formula}. Avec {parameter1}={value1} et {parameter2}={value2}, on obtient {result}."
    EXPLANATION_DIVERS = "Pour résoudre ce problème, on procède ainsi: {steps}. La réponse est {result}."
    
    # Tags
    TAGS_ALGORITHMIC = "algorithmique,simple"
    TAGS_AI = "ia,generatif,starwars"
    
    # Réponses
    SUCCESS_ANSWER_CORRECT = "Bravo ! Ta réponse est correcte."
    ERROR_ANSWER_INCORRECT = "Ce n'est pas correct. Essaie encore !"
    
    # Création
    SUCCESS_EXERCISE_CREATED = "Exercice créé avec succès"
    ERROR_EXERCISE_CREATION = "Erreur lors de la création de l'exercice"
    
    # Autres messages
    INFO_EXERCISE_SUBMITTED = "Réponse soumise"
    INFO_EXERCISE_COMPLETE = "Exercice terminé"
    INFO_EXERCISE_SKIPPED = "Exercice passé"

# Éléments narratifs Star Wars pour les exercices générés par IA
class StarWarsNarratives:
    # Personnages Star Wars pour les contextes
    CHARACTERS = [
        "Luke Skywalker", "Princesse Leia", "Han Solo", "Chewbacca", "Maître Yoda", 
        "Obi-Wan Kenobi", "R2-D2", "C-3PO", "Darth Vader", "Rey", 
        "Kylo Ren", "BB-8", "Finn", "Poe Dameron", "Padmé Amidala", 
        "Qui-Gon Jinn", "Mace Windu", "Ahsoka Tano", "Boba Fett", "Le Mandalorien"
    ]
    
    # Objets Star Wars
    OBJECTS = [
        "sabres laser", "vaisseaux", "blasters", "droïdes", "cristaux kyber", 
        "pièces détachées", "crédits galactiques", "hologrammes", "speeders", "chasseurs X-wing", 
        "chasseurs TIE", "grenades thermiques", "jetpacks", "casques de stormtrooper"
    ]
    
    # Lieux Star Wars
    LOCATIONS = [
        "Tatooine", "Coruscant", "Endor", "Hoth", "Dagobah", 
        "Naboo", "Mustafar", "Alderaan", "Jakku", "Exegol", 
        "Cantina de Mos Eisley", "Temple Jedi", "l'Étoile de la Mort", "la Base Starkiller", "Geonosis"
    ]
    
    # Préfixes pour les explications (contexte et importance des mathématiques)
    EXPLANATION_PREFIXES = [
        "Dans l'univers Star Wars, il est important de partager équitablement les ressources, comme les armes laser.",
        "Les Jedi enseignent que la maîtrise des mathématiques est essentielle à l'équilibre de la Force.",
        "Comme le dit souvent Maître Yoda, 'Par les calculs, plus clair l'avenir devient.'",
        "Dans la galaxie lointaine, très lointaine, la précision des calculs peut faire la différence entre victoire et défaite.",
        "Pour un futur Jedi, comprendre les nombres est aussi important que manier le sabre laser.",
        "La Résistance utilise quotidiennement ce type de calcul pour planifier ses missions.",
        "L'Ordre Jedi a toujours valorisé les connaissances mathématiques dans la formation des Padawans.",
        "Dans les archives du Temple Jedi, ce genre de problème est considéré comme fondamental.",
        "Qu'on soit du côté lumineux ou obscur de la Force, ces compétences mathématiques sont universelles.",
        "Même les droïdes comme R2-D2 doivent maîtriser ces calculs pour naviguer dans l'hyperespace."
    ]
    
    # Conclusions pour les explications (encouragement et lien avec l'univers Star Wars)
    EXPLANATION_SUFFIXES = [
        "Cette compétence te rapproche du rang de Maître Jedi.",
        "En maîtrisant ces calculs, tu progresses sur le chemin de la Force.",
        "Que la Force des mathématiques soit avec toi, jeune Padawan.",
        "Comme dirait Maître Yoda: 'Apprendre toujours, nous devons.'",
        "Ces connaissances te serviront dans toute la galaxie.",
        "Continue ainsi, et tu pourras bientôt construire ton propre sabre laser.",
        "La maîtrise de ces calculs te distingue des simples recrues de l'Empire.",
        "Même un Seigneur Sith serait impressionné par ta maîtrise des nombres.",
        "La Résistance a besoin de cerveaux brillants comme le tien.",
        "Avec de telles compétences, même le Conseil Jedi pourrait te remarquer."
    ]

# Textes de l'interface
class InterfaceTexts:
    # En-tête
    HEADER_TITLE = "Mathakine"
    HEADER_SUBTITLE = "L'API Rebelle"
    
    # Menu principal
    MENU_HOME = "Accueil"
    MENU_EXERCISES = "Exercices"
    MENU_DASHBOARD = "Tableau de bord"
    MENU_NEW_EXERCISE = "Nouvel exercice"
    
    # Page d'accueil
    HOME_TITLE = "Bienvenue sur Mathakine"
    HOME_SUBTITLE = "La plateforme d'entraînement mathématique pour les Padawans"
    HOME_START_BUTTON = "Commencer l'entraînement"
    HOME_DASHBOARD_BUTTON = "Consulter vos progrès"
    
    # Page d'exercices
    EXERCISES_TITLE = "Bibliothèque d'exercices"
    EXERCISES_SUBTITLE = "Sélectionner un exercice pour commencer"
    EXERCISES_EMPTY = "Aucun exercice disponible"
    EXERCISES_FILTER_TITLE = "Filtrer les exercices"
    EXERCISES_FILTER_TYPE = "Type d'exercice"
    EXERCISES_FILTER_DIFFICULTY = "Niveau de difficulté"
    EXERCISES_FILTER_BUTTON = "Appliquer les filtres"
    EXERCISES_GENERATE_BUTTON = "Générer un nouvel exercice"
    EXERCISES_BACK_BUTTON = "Retour à la liste"
    
    # Tableau de bord
    DASHBOARD_TITLE = "Tableau de bord"
    DASHBOARD_SUBTITLE = "Suivez votre progression vers la maîtrise des mathématiques"
    DASHBOARD_TOTAL_EXERCISES = "Exercices réalisés"
    DASHBOARD_CORRECT_ANSWERS = "Réponses correctes"
    DASHBOARD_SUCCESS_RATE = "Taux de réussite"
    DASHBOARD_EXPERIENCE = "Points d'expérience"
    DASHBOARD_PROGRESS_TITLE = "Progression"
    DASHBOARD_RECENT_ACTIVITY = "Activité récente"
    DASHBOARD_ACTIVITY_EMPTY = "Aucune activité récente"
    
    # Pied de page
    FOOTER_TEXT = "Mathakine - Exerce-toi aux mathématiques de façon amusante !"
    FOOTER_GITHUB = "Projet GitHub"
    FOOTER_VERSION = "Version 3.0 - L'API Rebelle"
    
    # Boutons génériques
    BUTTON_SUBMIT = "Soumettre"
    BUTTON_CANCEL = "Annuler"
    BUTTON_CONFIRM = "Confirmer"
    BUTTON_NEXT = "Suivant"
    BUTTON_PREVIOUS = "Précédent"
    BUTTON_CLOSE = "Fermer"
    BUTTON_DELETE = "Supprimer"
    BUTTON_EDIT = "Modifier"
    BUTTON_SAVE = "Enregistrer"
    BUTTON_BACK = "Retour"
    BUTTON_REFRESH = "Actualiser"
    
    # En-têtes et titres de pages
    PAGE_TITLE_HOME = "Accueil | Mathakine"
    PAGE_TITLE_EXERCISES = "Exercices | Mathakine"
    PAGE_TITLE_DASHBOARD = "Tableau de bord | Mathakine"
    PAGE_TITLE_ERROR = "Erreur | Mathakine"
    
    # Boutons
    BUTTON_HOME = "Accueil"
    BUTTON_EXERCISES = "Exercices"
    BUTTON_DASHBOARD = "Tableau de bord"
    BUTTON_LOGIN = "Connexion"
    BUTTON_REGISTER = "Inscription"
    BUTTON_LOGOUT = "Déconnexion"
    BUTTON_GENERATE = "Générer un exercice"
    
    # Libellés
    LABEL_NAME = "Nom"
    LABEL_EMAIL = "Email"
    LABEL_PASSWORD = "Mot de passe"
    LABEL_CONFIRM_PASSWORD = "Confirmer le mot de passe"
    LABEL_EXERCISE_TYPE = "Type d'exercice"
    LABEL_DIFFICULTY = "Difficulté"
    LABEL_ANSWER = "Réponse"
    
    # Textes de page d'accueil
    HOME_WELCOME = "Bienvenue sur Mathakine - L'API Rebelle"
    HOME_DESCRIPTION = "Rejoins les forces rebelles et entraîne-toi avec des exercices mathématiques amusants et interactifs."
    
    # Messages de connexion/inscription
    LOGIN_TITLE = "Connexion"
    LOGIN_SUBTITLE = "Connecte-toi pour accéder à ton compte"
    REGISTER_TITLE = "Inscription"
    REGISTER_SUBTITLE = "Crée un compte pour commencer"
    
    # Textes du tableau de bord
    DASHBOARD_NO_DATA = "Pas encore de données disponibles. Commence à résoudre des exercices !"
    
    # Messages d'erreur
    ERROR_404_TITLE = "Page non trouvée"
    ERROR_404_MESSAGE = "La page que tu cherches n'existe pas ou a été déplacée."
    ERROR_500_TITLE = "Erreur serveur"
    ERROR_500_MESSAGE = "Une erreur s'est produite sur le serveur. Veuillez réessayer plus tard."

# Notifications
class NotificationMessages:
    INFO_LOGGED_IN = "Connexion réussie"
    INFO_LOGGED_OUT = "Déconnexion réussie"
    INFO_REGISTERED = "Inscription réussie"
    WARNING_SESSION_EXPIRED = "Ta session a expiré, reconnecte-toi"
    ERROR_INVALID_CREDENTIALS = "Email ou mot de passe incorrect"
    ERROR_EMAIL_EXISTS = "Cet email est déjà utilisé" 