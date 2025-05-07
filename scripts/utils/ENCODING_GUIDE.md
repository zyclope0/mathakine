# Guide de gestion de l'encodage

Ce document explique comment gérer l'encodage des caractères dans le projet Math Trainer, en particulier pour les caractères accentués en français.

## Problématique

Les caractères accentués (é, è, ê, à, etc.) peuvent causer des problèmes d'affichage ou de fonctionnement lorsqu'ils ne sont pas correctement encodés. Ces problèmes sont particulièrement importants dans un projet multilingue ou qui utilise des caractères non-ASCII.

## Standard d'encodage

Tous les fichiers texte du projet doivent utiliser l'encodage **UTF-8** sans BOM (Byte Order Mark). L'UTF-8 est le standard le plus largement utilisé et compatible pour l'encodage des caractères.

## Types de fichiers concernés

Les types de fichiers suivants doivent être en UTF-8 :
- Fichiers Python (.py)
- Fichiers HTML (.html)
- Fichiers CSS (.css)
- Fichiers JavaScript (.js)
- Fichiers Markdown (.md)
- Fichiers Batch (.bat)
- Fichiers PowerShell (.ps1)
- Fichiers de configuration (.env, .json, etc.)

## Détecter les problèmes d'encodage

Le projet inclut des outils pour détecter et corriger les problèmes d'encodage :

### Vérification de l'encodage

```bash
# Avec CMD
scripts\utils\check_encoding.bat

# Avec PowerShell
.\scripts\utils\Check-Encoding.ps1
```

Ce script analysera tous les fichiers texte du projet et signalera ceux qui ont des problèmes d'encodage.

## Corriger les problèmes d'encodage

### Correction automatique

Le script de vérification propose une correction automatique pour les fichiers avec des problèmes d'encodage. Cette correction fonctionne dans la plupart des cas, mais pas tous.

### Correction manuelle

Pour les cas où la correction automatique échoue, utilisez le script `fix_direct.py` qui crée un nouveau fichier avec l'encodage correct :

```bash
# Créer un fichier avec l'encodage correct
python scripts\utils\fix_direct.py
```

### Dans votre éditeur de code

La plupart des éditeurs de code modernes permettent de changer l'encodage d'un fichier :

#### Visual Studio Code
1. Cliquez sur l'encodage affiché dans la barre d'état (en bas à droite)
2. Sélectionnez "Save with Encoding"
3. Choisissez "UTF-8"

#### Notepad++
1. Menu "Encodage"
2. Sélectionnez "Encoder en UTF-8"
3. Sauvegardez le fichier

## Recommandations

1. **Toujours créer de nouveaux fichiers en UTF-8**
   - Configurez votre éditeur pour utiliser UTF-8 par défaut

2. **Déclarer l'encodage dans les fichiers Python**
   - Ajoutez cette ligne en haut de chaque fichier Python :
   ```python
   # -*- coding: utf-8 -*-
   ```

3. **Déclarer l'encodage dans les fichiers HTML**
   - Ajoutez cette balise dans l'en-tête :
   ```html
   <meta charset="UTF-8">
   ```

4. **Vérifier l'encodage avant de soumettre des modifications**
   - Exécutez le script de vérification avant chaque commit

## Résolution des problèmes courants

### Caractères accentués mal affichés dans le terminal

Si les caractères accentués s'affichent mal dans le terminal Windows, cela peut être dû à la configuration du terminal plutôt qu'aux fichiers eux-mêmes. Essayez de :

1. Changer la police du terminal pour une police qui supporte l'Unicode
2. Utiliser la commande `chcp 65001` pour passer en UTF-8 avant d'exécuter les scripts

### Erreurs "SyntaxError: Non-UTF-8 code" dans Python

Ces erreurs surviennent lorsqu'un fichier Python contient des caractères non UTF-8. Pour corriger :

1. Ouvrez le fichier dans un éditeur qui détecte l'encodage
2. Sauvegardez-le en UTF-8
3. Ajoutez `# -*- coding: utf-8 -*-` en haut du fichier

## Encodage dans les scripts d'exécution

Les scripts d'exécution (.bat, .ps1) doivent être particulièrement attentifs à l'encodage lorsqu'ils manipulent des chaînes contenant des caractères accentués. Dans les scripts batch, le préfixe `@echo off` ne garantit pas la prise en charge correcte de l'UTF-8 par le terminal.

Pour les scripts PowerShell, il est recommandé d'utiliser :

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

Pour assurer un affichage correct des caractères accentués. 