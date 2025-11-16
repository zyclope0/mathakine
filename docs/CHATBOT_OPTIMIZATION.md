# 🤖 Optimisation du Chatbot Mathakine

**Guide complet pour optimiser le chatbot pour les mathématiques et mathélogique**

---

## 📊 **COMPARAISON : CODE vs PLATEFORME OPENAI**

### ✅ **Approche 1 : Modifier le Code (Recommandé)**

**Avantages** :
- ✅ **Contrôle total** : Vous pouvez ajuster le prompt système à tout moment
- ✅ **Versioning** : Le prompt est versionné avec votre code (Git)
- ✅ **Tests** : Vous pouvez tester différentes versions facilement
- ✅ **Personnalisation** : Adaptation dynamique selon le contexte (âge détecté, historique, etc.)
- ✅ **Pas de dépendance externe** : Pas besoin de configurer quoi que ce soit sur OpenAI Platform
- ✅ **Multi-environnements** : Différents prompts pour dev/staging/prod
- ✅ **Audit trail** : Vous voyez exactement ce qui est envoyé à OpenAI

**Inconvénients** :
- ⚠️ **Tokens système** : Chaque requête inclut le prompt système complet (coût)
- ⚠️ **Maintenance** : Vous devez gérer le prompt dans votre code

**Recommandation** : ✅ **Utiliser cette approche** pour Mathakine car :
- Vous avez besoin de personnalisation dynamique (détection d'âge)
- Vous voulez garder le contrôle sur le comportement
- Vous pouvez optimiser les coûts en ajustant `max_tokens`

---

### 🔧 **Approche 2 : Utiliser OpenAI Platform (Custom Instructions)**

**Avantages** :
- ✅ **Simplicité** : Configuration une fois sur la plateforme
- ✅ **Pas de code** : Pas besoin de modifier le code pour changer le comportement
- ✅ **Tokens économisés** : Le prompt système n'est pas envoyé à chaque requête (si utilisé avec Custom Instructions)

**Inconvénients** :
- ❌ **Pas de versioning** : Difficile de suivre les changements
- ❌ **Pas de tests** : Difficile de tester différentes versions
- ❌ **Pas de personnalisation dynamique** : Impossible d'adapter selon le contexte
- ❌ **Dépendance externe** : Configuration externe à votre code
- ❌ **Pas de multi-environnements** : Même configuration pour dev/prod

**Recommandation** : ❌ **Ne pas utiliser** pour Mathakine car :
- Vous avez besoin de personnalisation dynamique (détection d'âge)
- Vous voulez garder le contrôle versionné
- Vous avez besoin de différents comportements selon l'environnement

---

## 🎯 **OPTIMISATIONS APPLIQUÉES**

### **1. Prompt Système Optimisé**

Le prompt système a été amélioré avec :

- ✅ **Règles strictes** : Domaine mathématique/logique uniquement
- ✅ **Stratégie de redirection** : Message standard pour questions hors sujet
- ✅ **Adaptation par âge** : Langage adapté selon l'âge (5-8, 9-12, 13-16, 17-20 ans)
- ✅ **Style TSA/TDAH** : Langage simple, direct, prévisible
- ✅ **Exemples concrets** : Exemples de bonnes réponses pour guider l'IA
- ✅ **Règles strictes** : 7 règles claires à suivre

### **2. Paramètres OpenAI Optimisés**

```python
temperature=0.5,        # Réduit de 0.7 → plus cohérent, moins créatif
max_tokens=250,         # Réduit de 300 → plus concis (adapté TSA/TDAH)
top_p=0.9,              # Contrôle la diversité (0.9 = assez focalisé)
frequency_penalty=0.3,  # Encourage la variété dans le vocabulaire
presence_penalty=0.1,   # Encourage à rester sur le sujet
```

**Pourquoi ces valeurs ?**
- `temperature=0.5` : Réponses plus prévisibles et cohérentes (important pour TSA/TDAH)
- `max_tokens=250` : Réponses concises (évite la surcharge cognitive)
- `presence_penalty=0.1` : Encourage à rester sur le sujet mathématique

### **3. Détection d'Âge Automatique**

Le système détecte automatiquement l'âge approximatif depuis le message :

```python
# Détection basique (améliorable)
- Mots-clés : 'cm1', 'cm2', 'cp' → 5-8 ans
- Mots-clés : '6ème', '5ème', 'collège' → 9-12 ans
- Mots-clés : '4ème', '3ème', 'lycée' → 13-16 ans
- Mots-clés : 'terminale', 'bac' → 17-20 ans
```

**Améliorations futures possibles** :
- Détection depuis le profil utilisateur (si disponible)
- Analyse du niveau de langage utilisé
- Historique des questions pour affiner l'estimation

---

## 🚀 **AMÉLIORATIONS FUTURES POSSIBLES**

### **1. Système de Modération Avancé**

```python
# Filtrer les questions hors sujet AVANT d'appeler OpenAI
def is_math_related(message: str) -> bool:
    math_keywords = ['calcul', 'math', 'nombre', 'fraction', 'équation', ...]
    return any(keyword in message.lower() for keyword in math_keywords)
```

### **2. Contexte Utilisateur Enrichi**

```python
# Ajouter le niveau de l'utilisateur au contexte
user_level = get_user_level(user_id)  # 'initie', 'padawan', 'chevalier', 'maitre'
system_prompt += f"\n\nL'utilisateur est au niveau {user_level}. Adapte la difficulté."
```

### **3. Historique Intelligent**

```python
# Analyser l'historique pour détecter les patterns
# Exemple : Si l'utilisateur pose souvent des questions sur les fractions,
# proposer des exercices sur les fractions
```

### **4. Feedback Loop**

```python
# Permettre à l'utilisateur de noter la réponse
# Utiliser ces notes pour améliorer le prompt système
```

### **5. Multi-langues**

```python
# Détecter la langue et adapter le prompt système
if user_language == 'en':
    system_prompt = english_system_prompt
```

---

## 📝 **EXEMPLES DE PROMPTS OPTIMISÉS**

### **Exemple 1 : Question Simple (5-8 ans)**

**Question** : "Comment faire 3 + 2 ?"

**Réponse attendue** :
```
3 + 2 = 5 ! Imagine que tu as 3 pommes et que tu en ajoutes 2. 
Tu auras 5 pommes au total. 🍎 Bravo pour ta question !
```

### **Exemple 2 : Concept Mathématique (9-12 ans)**

**Question** : "C'est quoi une fraction ?"

**Réponse attendue** :
```
Une fraction, c'est une partie d'un tout ! Par exemple, si tu manges 
la moitié d'une pizza, tu manges 1/2 de la pizza. Le chiffre du haut 
(numérateur) dit combien de parts tu prends, celui du bas (dénominateur) 
dit en combien de parts le tout est divisé.
```

### **Exemple 3 : Question Hors Sujet**

**Question** : "Quelle est la capitale de la France ?"

**Réponse attendue** :
```
Je suis spécialisé en mathématiques et logique ! Je peux t'aider avec 
des calculs, des problèmes mathématiques, ou des défis logiques. 
Peux-tu me poser une question sur les maths ? 🧮
```

---

## 🎓 **BONNES PRATIQUES**

### **1. Tester Régulièrement**

Testez le chatbot avec différents types de questions :
- ✅ Questions mathématiques simples
- ✅ Questions mathématiques complexes
- ✅ Questions hors sujet (pour vérifier la redirection)
- ✅ Questions ambiguës

### **2. Monitorer les Réponses**

Surveillez les réponses du chatbot pour détecter :
- Des dérives hors sujet
- Des réponses trop longues/complexes
- Des réponses inadaptées à l'âge

### **3. Itérer sur le Prompt**

Le prompt système peut être amélioré en continu :
- Ajouter des exemples de bonnes réponses
- Affiner les règles strictes
- Adapter selon les retours utilisateurs

### **4. Optimiser les Coûts**

- Réduire `max_tokens` si les réponses sont trop longues
- Utiliser `gpt-4o-mini` pour réduire les coûts (déjà configuré)
- Monitorer l'utilisation des tokens

---

## 🔍 **MONITORING ET ANALYTICS**

### **Métriques à Suivre**

1. **Taux de redirection** : % de questions hors sujet redirigées
2. **Longueur moyenne des réponses** : Doit rester < 250 tokens
3. **Satisfaction utilisateur** : Si vous ajoutez un système de notation
4. **Coût par conversation** : Monitorer les tokens utilisés

### **Logs Recommandés**

```python
# Logger les requêtes importantes
logger.info(f"Chat request - Age: {estimated_age}, Tokens: {response.usage.total_tokens}")
```

---

## ✅ **CONCLUSION**

**Approche recommandée** : ✅ **Modifier le code**

Le prompt système optimisé dans `server/handlers/chat_handlers.py` est maintenant :
- ✅ Focalisé sur les mathématiques uniquement
- ✅ Adapté aux enfants TSA/TDAH (langage simple, direct)
- ✅ Adaptatif selon l'âge détecté
- ✅ Optimisé avec les bons paramètres OpenAI

**Prochaines étapes** :
1. Tester le chatbot avec différents types de questions
2. Monitorer les réponses et ajuster si nécessaire
3. Implémenter les améliorations futures (détection d'âge depuis profil, etc.)

---

**Date de création** : Janvier 2025  
**Dernière mise à jour** : Janvier 2025

