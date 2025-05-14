# Structure CSS du projet Mathakine

Ce répertoire contient tous les fichiers CSS utilisés dans le projet Mathakine. Une réorganisation a été effectuée pour normaliser et améliorer la maintenabilité du code CSS.

## Organisation des fichiers

Les fichiers CSS sont organisés comme suit :

1. **normalize.css** - Réinitialisation CSS standardisée
   - Normalise le rendu entre les navigateurs
   - Contient des réinitialisations de base pour les éléments HTML
   - Ajoute quelques améliorations d'accessibilité

2. **variables.css** - Variables CSS globales
   - Définit toutes les variables CSS utilisées dans le projet
   - Couleurs, espacements, typographie, effets, etc.
   - Point central pour les modifications de style global

3. **utils.css** - Classes utilitaires
   - Contient des classes réutilisables pour les mises en page communes
   - Marges, paddings, alignements, flexbox, etc.
   - Remplace la plupart des styles en ligne dans le HTML

4. **style.css** - Styles principaux de l'application
   - Styles de base pour les composants principaux
   - Importe les autres fichiers CSS (normalize, variables, utils)
   - Définit les styles des éléments communs à toutes les pages

5. **space-theme.css** - Thème Star Wars
   - Styles spécifiques au thème spatial Star Wars
   - Surcharge les styles de base pour appliquer le thème
   - Effets visuels spécifiques au thème

6. **home-styles.css** - Styles spécifiques à la page d'accueil
   - Chargé uniquement sur la page d'accueil
   - Styles pour les sections spécifiques (hero, features, etc.)

## Bonnes pratiques à suivre

1. **Utiliser les variables CSS**
   - Toujours utiliser les variables définies dans `variables.css`
   - Ne pas utiliser de valeurs codées en dur

2. **Privilégier les classes utilitaires**
   - Utiliser les classes utilitaires de `utils.css` quand possible
   - Ne pas ajouter de styles en ligne dans le HTML

3. **Respecter l'organisation des fichiers**
   - Ajouter les variables globales dans `variables.css`
   - Ajouter les classes utilitaires dans `utils.css`
   - Ajouter les styles spécifiques à un composant dans `style.css`
   - Ajouter les styles du thème Star Wars dans `space-theme.css`

4. **Ordre d'importation**
   - Toujours respecter l'ordre d'importation dans le HTML:
     1. normalize.css
     2. variables.css  
     3. utils.css
     4. style.css
     5. space-theme.css
     6. Autres fichiers spécifiques (home-styles.css, etc.)

## Script de normalisation

Un script utilitaire a été créé pour normaliser les styles en ligne dans les fichiers HTML:

```
python scripts/normalize_css.py
```

Ce script remplace les styles en ligne par des classes utilitaires appropriées.

## Exemple d'utilisation des classes utilitaires

Au lieu de :
```html
<div style="display: flex; justify-content: space-between; margin-top: 20px;">
```

Préférer :
```html
<div class="d-flex justify-between mt-3">
``` 