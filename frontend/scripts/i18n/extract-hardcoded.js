#!/usr/bin/env node

/**
 * Script d'extraction des textes hardcodés
 * Scanne les fichiers pour détecter les textes français hardcodés
 * Génère un rapport des textes à traduire
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// Patterns pour détecter le texte français
const FRENCH_PATTERNS = [
  // Mots français courants
  /\b(Connexion|Inscription|Déconnexion|Exercices|Défis|Badges|Tableau de bord)\b/gi,
  // Phrases françaises courantes
  /\b(Nom d'utilisateur|Mot de passe|Valider|Annuler|Enregistrer)\b/gi,
  // Textes avec accents
  /[éèêàçôùûîïë]/gi,
  // Phrases complètes françaises
  /(Choisissez|Générez|Résoudre|Accédez|Bienvenue)/gi,
];

// Extensions de fichiers à scanner
const EXTENSIONS = [".tsx", ".ts", ".jsx", ".js"];

// Dossiers à scanner
const SCAN_DIRS = [path.join(__dirname, "../../app"), path.join(__dirname, "../../components")];

// Dossiers à ignorer
const IGNORE_DIRS = ["node_modules", ".next", "__tests__", "api"];

// Fonction pour vérifier si un fichier doit être ignoré
function shouldIgnore(filePath) {
  return IGNORE_DIRS.some((dir) => filePath.includes(dir));
}

// Fonction pour extraire les textes hardcodés d'un fichier
function extractHardcodedTexts(filePath) {
  const content = fs.readFileSync(filePath, "utf8");
  const lines = content.split("\n");
  const findings = [];

  lines.forEach((line, index) => {
    // Ignorer les commentaires et les imports
    if (
      line.trim().startsWith("//") ||
      line.trim().startsWith("/*") ||
      line.trim().startsWith("*") ||
      line.trim().startsWith("import") ||
      line.trim().startsWith("export")
    ) {
      return;
    }

    // Chercher les chaînes de caractères
    const stringMatches = line.match(/["'`]([^"'`]+)["'`]/g);

    if (stringMatches) {
      stringMatches.forEach((match) => {
        const text = match.slice(1, -1); // Enlever les guillemets

        // Vérifier si c'est du français
        const isFrench = FRENCH_PATTERNS.some((pattern) => pattern.test(text));

        // Ignorer les URLs, chemins, classes CSS, etc.
        const isIgnorable =
          text.startsWith("http") ||
          text.startsWith("/") ||
          text.startsWith("./") ||
          text.startsWith("../") ||
          text.includes("className") ||
          text.includes("class=") ||
          text.match(/^[a-z-]+$/i) || // Classes CSS simples
          text.match(/^[A-Z][a-zA-Z]*$/) || // Noms de composants
          text.length < 3; // Trop court

        if (isFrench && !isIgnorable && text.length > 2) {
          findings.push({
            file: filePath,
            line: index + 1,
            text: text,
            context: line.trim(),
          });
        }
      });
    }
  });

  return findings;
}

// Fonction pour scanner un répertoire
function scanDirectory(dirPath, findings = []) {
  if (!fs.existsSync(dirPath)) {
    return findings;
  }

  const entries = fs.readdirSync(dirPath, { withFileTypes: true });

  entries.forEach((entry) => {
    const fullPath = path.join(dirPath, entry.name);

    if (shouldIgnore(fullPath)) {
      return;
    }

    if (entry.isDirectory()) {
      scanDirectory(fullPath, findings);
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name);
      if (EXTENSIONS.includes(ext)) {
        const fileFindings = extractHardcodedTexts(fullPath);
        findings.push(...fileFindings);
      }
    }
  });

  return findings;
}

// Fonction pour suggérer un namespace
function suggestNamespace(filePath) {
  if (
    filePath.includes("/login") ||
    filePath.includes("/register") ||
    filePath.includes("/forgot-password")
  ) {
    return "auth";
  }
  if (filePath.includes("/exercises") || filePath.includes("/exercise/")) {
    return "exercises";
  }
  if (filePath.includes("/challenges") || filePath.includes("/challenge/")) {
    return "challenges";
  }
  if (filePath.includes("/dashboard")) {
    return "dashboard";
  }
  if (filePath.includes("/badges")) {
    return "badges";
  }
  if (filePath.includes("/components/")) {
    return "common";
  }
  return "common";
}

// Fonction principale
function extractHardcoded() {
  console.log("🔍 Extraction des textes hardcodés...\n");

  const allFindings = [];

  SCAN_DIRS.forEach((dir) => {
    console.log(`📁 Scan de ${dir}...`);
    const findings = scanDirectory(dir);
    allFindings.push(...findings);
  });

  console.log(`\n📊 Résultats:`);
  console.log(`   - ${allFindings.length} textes hardcodés détectés\n`);

  if (allFindings.length === 0) {
    console.log("✅ Aucun texte hardcodé détecté !");
    return 0;
  }

  // Grouper par fichier
  const byFile = {};
  allFindings.forEach((finding) => {
    if (!byFile[finding.file]) {
      byFile[finding.file] = [];
    }
    byFile[finding.file].push(finding);
  });

  // Afficher les résultats
  console.log("📝 Textes hardcodés détectés:\n");

  Object.keys(byFile).forEach((file) => {
    const relativePath = path.relative(path.join(__dirname, "../.."), file);
    const namespace = suggestNamespace(file);

    console.log(`📄 ${relativePath}`);
    console.log(`   Namespace suggéré: ${namespace}`);

    byFile[file].forEach((finding) => {
      console.log(`   Ligne ${finding.line}: "${finding.text}"`);
      console.log(`   Contexte: ${finding.context.substring(0, 80)}...`);
    });

    console.log("");
  });

  // Générer un rapport JSON
  const reportPath = path.join(__dirname, "../../hardcoded-texts-report.json");
  fs.writeFileSync(reportPath, JSON.stringify(byFile, null, 2));
  console.log(`📄 Rapport JSON généré: ${reportPath}\n`);

  console.log("💡 Suggestions:");
  console.log("   1. Vérifier si les traductions existent déjà dans messages/fr.json");
  console.log("   2. Ajouter les traductions manquantes");
  console.log("   3. Remplacer les textes hardcodés par useTranslations()");
  console.log("   4. Relancer ce script pour vérifier\n");

  return allFindings.length > 0 ? 1 : 0;
}

// Exécuter le script
if (require.main === module) {
  const exitCode = extractHardcoded();
  process.exit(exitCode);
}

module.exports = { extractHardcoded };
