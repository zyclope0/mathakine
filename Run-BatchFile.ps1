<#
.SYNOPSIS
    Wrapper pour exécuter des fichiers batch depuis PowerShell
.DESCRIPTION
    Ce script facilite l'exécution des fichiers batch (.bat) depuis PowerShell
    en contournant les problèmes de compatibilité
.PARAMETER BatchFile
    Chemin vers le fichier batch à exécuter
.EXAMPLE
    .\Run-BatchFile.ps1 -BatchFile "start_direct.bat"
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$BatchFile
)

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Exécution du fichier batch: $BatchFile" -ForegroundColor Cyan  
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host

$batchPath = $BatchFile
if (-not (Test-Path $batchPath)) {
    Write-Host "Le fichier '$BatchFile' n'existe pas!" -ForegroundColor Red
    exit 1
}

Write-Host "Exécution en cours..." -ForegroundColor Yellow

# Utiliser cmd.exe pour exécuter le fichier batch
cmd.exe /c "$batchPath"

Write-Host
Write-Host "Exécution terminée." -ForegroundColor Green
Write-Host
Write-Host "Appuyez sur une touche pour continuer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 