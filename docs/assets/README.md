# Assets de documentation

Ce dossier contient les ressources visuelles utilisées dans la documentation.

## Structure

```
assets/
├── images/              # Images et captures d'écran
│   ├── main_interface.png
│   ├── dashboard.png
│   └── exercise.png
├── diagrams/           # Diagrammes source (si nécessaire)
└── icons/             # Icônes et logos
```

## Conventions de nommage

- Utiliser des noms en minuscules
- Séparer les mots par des underscores
- Préfixer les captures d'écran avec la date : `YYYYMMDD_description.png`
- Utiliser des formats optimisés (PNG pour captures, SVG pour icônes)

## Mise à jour des images

1. Pour mettre à jour une capture d'écran :
   - Faire la capture en résolution 1920x1080
   - Optimiser l'image (compression sans perte)
   - Nommer selon la convention
   - Mettre à jour la date dans le nom

2. Pour les diagrammes :
   - Conserver les sources dans `/diagrams`
   - Exporter en PNG pour la documentation
   - Mettre à jour ARCHITECTURE_DIAGRAMS.md

## Maintenance

- Vérifier régulièrement la pertinence des captures
- Supprimer les images obsolètes
- Maintenir une taille de dossier raisonnable
- Compresser les images volumineuses

---

*Dernière mise à jour : 15 juin 2025* 