# Guide PowerShell vs Batch

Ce guide présente les principales différences entre les scripts Batch (.bat) et PowerShell (.ps1) utilisés dans ce projet.

## Différences fondamentales

| Fonctionnalité | Batch (.bat) | PowerShell (.ps1) |
|----------------|--------------|-------------------|
| **Variables** | `set VAR=valeur` | `$VAR = "valeur"` |
| **Commentaires** | `REM commentaire` ou `:: commentaire` | `# commentaire` |
| **Comparaison** | `if "%VAR%"=="valeur"` | `if ($VAR -eq "valeur")` |
| **Exécution** | Directement dans CMD | Requiert politique d'exécution |
| **Affichage** | `echo message` | `Write-Host "message"` |
| **Redirection** | `>null 2>&1` | `Out-Null` |
| **Encodage** | ANSI/ASCII | UTF-8 avec BOM |

## Exécution de scripts PowerShell

Dans ce projet, nous fournissons un wrapper pour faciliter l'exécution des scripts PowerShell :

```batch
run_ps1.bat script.ps1 [arguments]
```

Ce wrapper utilise `-ExecutionPolicy Bypass` pour contourner les restrictions d'exécution de PowerShell.

## Exemples comparatifs

### Variables et conditions

**Batch**
```batch
@echo off
set "NAME=Math Trainer"
if "%NAME%"=="Math Trainer" (
    echo Le nom est Math Trainer
) else (
    echo Le nom est différent
)
```

**PowerShell**
```powershell
$Name = "Math Trainer"
if ($Name -eq "Math Trainer") {
    Write-Host "Le nom est Math Trainer"
} else {
    Write-Host "Le nom est différent"
}
```

### Boucles

**Batch**
```batch
@echo off
for %%i in (1 2 3 4 5) do (
    echo Numéro %%i
)
```

**PowerShell**
```powershell
foreach ($i in 1..5) {
    Write-Host "Numéro $i"
}
```

### Traitement de fichiers

**Batch**
```batch
@echo off
if exist "fichier.txt" (
    echo Le fichier existe
) else (
    echo > fichier.txt
    echo Fichier créé
)
```

**PowerShell**
```powershell
if (Test-Path "fichier.txt") {
    Write-Host "Le fichier existe"
} else {
    Set-Content -Path "fichier.txt" -Value ""
    Write-Host "Fichier créé"
}
```

## Avantages de PowerShell

- **Objets** : PowerShell manipule des objets plutôt que du texte
- **Compatibilité .NET** : Accès à toutes les fonctionnalités .NET
- **Commandes avancées** : Plus de 200 cmdlets intégrées
- **Traitement JSON/XML** : Support natif des formats structurés
- **Sécurité** : Contrôle d'exécution plus strict
- **Syntaxe moderne** : Plus cohérente et lisible

## Avantages de Batch

- **Disponibilité** : Fonctionne sur toutes les versions de Windows sans installation
- **Simplicité** : Syntaxe plus simple pour les tâches basiques
- **Performances** : Démarrage plus rapide pour les scripts courts
- **Compatibilité** : Fonctionne même sur les anciens systèmes

## Quand utiliser quoi ?

- **Utilisez Batch** pour les scripts simples ou les lanceurs qui doivent fonctionner partout
- **Utilisez PowerShell** pour les tâches complexes nécessitant une logique avancée

Dans ce projet, nous fournissons les deux versions pour maximiser la compatibilité tout en offrant des fonctionnalités avancées pour ceux qui peuvent utiliser PowerShell. 