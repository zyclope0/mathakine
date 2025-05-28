"""
Messages et textes centralisés pour l'application Mathakine
Ce fichier contient tous les messages et textes utilisés dans l'application.
"""

import random

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
    ERROR_DATABASE = "Erreur de base de données"
    
    # Succès
    SUCCESS_OPERATION_COMPLETED = "Opération réussie"
    SUCCESS_CREATED = "Ressource créée avec succès"
    SUCCESS_UPDATED = "Ressource mise à jour avec succès"
    SUCCESS_DELETED = "Ressource supprimée avec succès"
    SUCCESS_ARCHIVED = "Exercice archivé avec succès"
    
    # Messages d'information
    INFO_TRYING_CONNECTION = "Tentative de connexion à la base de données"
    INFO_APP_STARTING = "Démarrage de l'application"
    INFO_APP_READY = "Application prête"
    INFO_APP_STOPPING = "Arrêt de l'application"

# Messages liés aux exercices
class ExerciseMessages:
    # Titres des exercices
    TITLE_ADDITION = "Addition galactique"
    TITLE_SUBTRACTION = "Soustraction stellaire"
    TITLE_MULTIPLICATION = "Multiplication cosmique"
    TITLE_DIVISION = "Division spatiale"
    TITLE_FRACTIONS = "Fractions de l'hyperespace"
    TITLE_GEOMETRIE = "Géométrie des constellations"
    TITLE_DIVERS = "Défi mathématique"
    TITLE_DEFAULT = "Exercice mathématique"
    TITLE_AI_PREFIX = "TEST-ZAXXON"
    
    # Messages de résultats
    RESULT_CORRECT = "Excellent travail ! Ta réponse est correcte."
    RESULT_INCORRECT = "Pas tout à fait ! Essaie encore."
    RESULT_HINT = "Indice: {hint}"
    
    # Questions types
    QUESTION_ADDITION = "Calcule {num1} + {num2}"
    QUESTION_SUBTRACTION = "Calcule {num1} - {num2}"
    QUESTION_MULTIPLICATION = "Calcule {num1} × {num2}"
    QUESTION_DIVISION = "Calcule {num1} ÷ {num2}"
    QUESTION_FRACTIONS = "Calcule {num1}/{num2} {operation} {num3}/{num4}"
    QUESTION_GEOMETRIE = "Calcule le {property} du {shape} avec {parameter1}={value1} et {parameter2}={value2}"
    QUESTION_DIVERS = "{problem}"
    
    # Textes éducatifs
    EXPLANATION_ADDITION = "{num1} + {num2} = {result}"
    EXPLANATION_SUBTRACTION = "{num1} - {num2} = {result}"
    EXPLANATION_MULTIPLICATION = "{num1} × {num2} = {result}"
    EXPLANATION_DIVISION = "{num1} ÷ {num2} = {result}"
    EXPLANATION_FRACTIONS = "Pour calculer {num1}/{num2} {operation} {num3}/{num4}, il faut {steps}. Le résultat est {result}."
    EXPLANATION_GEOMETRIE = "Pour calculer le {property} du {shape}, on utilise la formule: {formula}. Avec {parameter1}={value1} et {parameter2}={value2}, on obtient {result}."
    EXPLANATION_DIVERS = "Voici comment résoudre ce problème: {steps}. La réponse est {result}."
    
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
    
    # Préfixes pour les explications - OPTIMISÉS par difficulté
    EXPLANATION_PREFIXES = {
        "INITIE": [
            "Jeune Padawan, comme l'enseigne Maître Yoda :",
            "Dans tes premiers pas vers la maîtrise de la Force :",
            "Pour un apprenti Jedi, cette leçon est fondamentale :",
            "R2-D2 bipe d'approbation car :",
            "Luke a appris cette technique de base :",
            "C-3PO calcule que :",
        ],
        "PADAWAN": [
            "En progressant dans ta formation Jedi :",
            "Les archives du Temple enseignent que :",
            "Comme l'a découvert Anakin Skywalker :",
            "La Résistance utilise cette stratégie car :",
            "Obi-Wan explique à ses élèves que :",
            "Dans les missions de reconnaissance :",
        ],
        "CHEVALIER": [
            "Un Chevalier Jedi maîtrise ces calculs car :",
            "Dans les batailles galactiques complexes :",
            "Le Conseil Jedi reconnaît l'importance de :",
            "Lors des missions diplomatiques critiques :",
            "Les stratèges de l'Alliance savent que :",
            "Face aux défis de l'Empire :",
        ],
        "MAITRE": [
            "Un Maître Jedi comprend que :",
            "Dans la sagesse millénaire de l'Ordre :",
            "Les grands stratèges galactiques enseignent :",
            "Face aux mystères de la Force :",
            "Dans les décisions qui façonnent la galaxie :",
            "Comme l'ont prouvé les anciens Maîtres :",
        ]
    }
    
    # Conclusions pour les explications - OPTIMISÉES par difficulté
    EXPLANATION_SUFFIXES = {
        "INITIE": [
            "Continue ainsi, jeune Padawan !",
            "Tu progresses bien dans ta formation.",
            "La Force grandit en toi.",
            "Même R2-D2 est impressionné !",
            "Tu es sur la bonne voie vers la maîtrise.",
            "Que la Force t'accompagne dans tes calculs.",
        ],
        "PADAWAN": [
            "Tu maîtrises les bases comme un vrai Jedi.",
            "Tes compétences s'affinent, continue !",
            "La voie du Jedi s'éclaire devant toi.",
            "Tu honores l'enseignement de tes Maîtres.",
            "Ces connaissances te serviront dans tes missions.",
            "Tu progresses vers le rang de Chevalier.",
        ],
        "CHEVALIER": [
            "Digne d'un Chevalier Jedi accompli.",
            "Ta maîtrise égale celle des grands stratèges.",
            "Le Conseil Jedi serait fier de tes progrès.",
            "Tu démontres la sagesse d'un vrai Jedi.",
            "Ces compétences te distinguent dans la galaxie.",
            "Tu es prêt pour les défis les plus complexes.",
        ],
        "MAITRE": [
            "Sagesse digne d'un Maître Jedi.",
            "Tu atteins les sommets de la connaissance.",
            "Même Yoda approuverait ta maîtrise.",
            "Ta sagesse éclairera les générations futures.",
            "Tu incarnes l'excellence de l'Ordre Jedi.",
            "Que ta sagesse guide la galaxie vers la paix.",
        ]
    }
    
    # Préfixes génériques (fallback pour compatibilité)
    EXPLANATION_PREFIXES_GENERIC = [
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
    
    # Suffixes génériques (fallback pour compatibilité)
    EXPLANATION_SUFFIXES_GENERIC = [
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

    # Contextes spécialisés par type d'exercice
    CONTEXTS_BY_TYPE = {
        "ADDITION": {
            "objects": ["cristaux Kyber", "vaisseaux rebelles", "droïdes", "soldats", "crédits"],
            "actions": ["rejoignent", "s'allient", "se rassemblent", "fusionnent", "s'unissent"],
            "locations": ["base rebelle", "cantina", "hangar", "temple Jedi", "station spatiale"]
        },
        "SUBTRACTION": {
            "objects": ["TIE Fighters", "stormtroopers", "ressources", "munitions", "vaisseaux"],
            "actions": ["sont détruits", "désertent", "sont perdus", "sont confisqués", "disparaissent"],
            "locations": ["bataille spatiale", "raid impérial", "mission secrète", "combat", "siège"]
        },
        "MULTIPLICATION": {
            "objects": ["escadrons", "bataillons", "flottes", "systèmes", "garnisons"],
            "actions": ["se multiplient", "se déploient", "s'organisent", "se coordonnent", "s'étendent"],
            "locations": ["secteur galactique", "front de guerre", "territoire", "zone d'influence", "région"]
        },
        "DIVISION": {
            "objects": ["ressources", "troupes", "équipements", "territoires", "responsabilités"],
            "actions": ["se répartissent", "se divisent", "se distribuent", "se partagent", "s'organisent"],
            "locations": ["bases", "planètes", "secteurs", "commandements", "divisions"]
        }
    }

    @classmethod
    def get_explanation_prefix(cls, difficulty="PADAWAN"):
        """Récupère un préfixe d'explication adapté à la difficulté"""
        prefixes = cls.EXPLANATION_PREFIXES.get(difficulty.upper(), cls.EXPLANATION_PREFIXES_GENERIC)
        return random.choice(prefixes)
    
    @classmethod
    def get_explanation_suffix(cls, difficulty="PADAWAN"):
        """Récupère un suffixe d'explication adapté à la difficulté"""
        suffixes = cls.EXPLANATION_SUFFIXES.get(difficulty.upper(), cls.EXPLANATION_SUFFIXES_GENERIC)
        return random.choice(suffixes)

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
    BUTTON_SUBMIT = "Valider"
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
    BUTTON_RETRY = "Réessayer"
    BUTTON_GENERATE = "Générer"
    BUTTON_ARCHIVE = "Archiver"
    
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
    
    # Libellés
    LABEL_NAME = "Nom"
    LABEL_EMAIL = "Email"
    LABEL_PASSWORD = "Mot de passe"
    LABEL_CONFIRM_PASSWORD = "Confirmer le mot de passe"
    LABEL_EXERCISE_TYPE = "Type d'exercice"
    LABEL_DIFFICULTY = "Niveau de difficulté"
    LABEL_ANSWER = "Ta réponse"
    
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

# Messages spécifiques aux utilisateurs
class UserMessages:
    # Connexion et inscription
    SUCCESS_REGISTRATION = "Inscription réussie ! Bienvenue dans l'Ordre Jedi."
    SUCCESS_LOGIN = "Connexion réussie ! Que la Force soit avec toi."
    SUCCESS_LOGOUT = "Déconnexion réussie. Que la Force te guide."
    ERROR_INVALID_CREDENTIALS = "Les informations d'identification sont incorrectes."
    ERROR_USERNAME_EXISTS = "Ce nom d'utilisateur est déjà pris."
    ERROR_EMAIL_EXISTS = "Cette adresse email est déjà utilisée."
    ERROR_PASSWORD_MISMATCH = "Les mots de passe ne correspondent pas."
    ERROR_INACTIVE_ACCOUNT = "Ce compte a été désactivé."
    
    # Validation des champs
    ERROR_PASSWORD_WEAK = "Le mot de passe doit contenir au moins 8 caractères, une majuscule et un chiffre."
    ERROR_USERNAME_INVALID = "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores."
    ERROR_EMAIL_INVALID = "L'adresse email n'est pas valide."
    
    # Profil utilisateur
    SUCCESS_PROFILE_UPDATE = "Profil mis à jour avec succès."
    SUCCESS_PASSWORD_UPDATE = "Mot de passe mis à jour avec succès."
    ERROR_CURRENT_PASSWORD = "Le mot de passe actuel est incorrect."
    
    # Permissions
    ERROR_NOT_AUTHORIZED = "Tu n'es pas autorisé à effectuer cette action."
    ERROR_ADMIN_REQUIRED = "Seuls les administrateurs peuvent effectuer cette action."
    ERROR_GARDIEN_REQUIRED = "Seuls les Gardiens et Archivistes peuvent effectuer cette action."
    ERROR_CHEVALIER_REQUIRED = "Seuls les Chevaliers Jedi et supérieurs peuvent effectuer cette action."
    
    # Progression
    SUCCESS_PROGRESS_RESET = "Ta progression a été réinitialisée."
    INFO_LEVEL_UP = "Félicitations ! Tu as atteint le niveau {level}."
    INFO_ACHIEVEMENT_UNLOCKED = "Nouvel accomplissement débloqué : {achievement}"
    
    # Gestion des utilisateurs
    SUCCESS_USER_CREATED = "Utilisateur créé avec succès."
    SUCCESS_USER_UPDATED = "Utilisateur mis à jour avec succès."
    SUCCESS_USER_DELETED = "Utilisateur supprimé avec succès."
    ERROR_USER_NOT_FOUND = "Utilisateur non trouvé."
    ERROR_CANNOT_DELETE_SELF = "Vous ne pouvez pas supprimer votre propre compte." 