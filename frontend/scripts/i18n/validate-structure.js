#!/usr/bin/env node

/**
 * Script de validation de la structure des fichiers de traduction
 * Valide la syntaxe JSON et la cohérence des structures
 */

const fs = require("fs");
const path = require("path");

const FR_FILE = path.join(__dirname, "../../messages/fr.json");
const EN_FILE = path.join(__dirname, "../../messages/en.json");

// Fonction pour valider la syntaxe JSON
function validateJSON(filePath) {
  try {
    const content = fs.readFileSync(filePath, "utf8");
    const parsed = JSON.parse(content);
    return { valid: true, data: parsed, error: null };
  } catch (error) {
    return { valid: false, data: null, error: error.message };
  }
}

// Fonction pour obtenir la profondeur maximale d'un objet
function getMaxDepth(obj, currentDepth = 0) {
  if (typeof obj !== "object" || obj === null || Array.isArray(obj)) {
    return currentDepth;
  }

  let maxDepth = currentDepth;
  for (const key in obj) {
    const depth = getMaxDepth(obj[key], currentDepth + 1);
    if (depth > maxDepth) {
      maxDepth = depth;
    }
  }

  return maxDepth;
}

// Fonction pour compter les clés
function countKeys(obj) {
  let count = 0;

  for (const key in obj) {
    count++;
    if (typeof obj[key] === "object" && obj[key] !== null && !Array.isArray(obj[key])) {
      count += countKeys(obj[key]);
    }
  }

  return count;
}

// Fonction pour trouver les valeurs vides
function findEmptyValues(obj, prefix = "") {
  const empty = [];

  for (const key in obj) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    const value = obj[key];

    if (value === null || value === undefined || value === "") {
      empty.push(fullKey);
    } else if (typeof value === "object" && !Array.isArray(value)) {
      empty.push(...findEmptyValues(value, fullKey));
    }
  }

  return empty;
}

// Fonction principale
function validateStructure() {
  console.log("🔍 Validation de la structure des traductions...\n");

  // Valider fr.json
  console.log("📄 Validation de fr.json...");
  const frValidation = validateJSON(FR_FILE);

  if (!frValidation.valid) {
    console.error(`❌ Erreur de syntaxe JSON dans fr.json: ${frValidation.error}`);
    return 1;
  }

  const frData = frValidation.data;
  const frDepth = getMaxDepth(frData);
  const frKeyCount = countKeys(frData);
  const frEmpty = findEmptyValues(frData);

  console.log(`   ✅ Syntaxe JSON valide`);
  console.log(`   📊 Profondeur maximale: ${frDepth}`);
  console.log(`   📊 Nombre de clés: ${frKeyCount}`);

  if (frEmpty.length > 0) {
    console.log(`   ⚠️  Valeurs vides détectées: ${frEmpty.length}`);
    frEmpty.forEach((key) => console.log(`      - ${key}`));
  }

  console.log("");

  // Valider en.json
  console.log("📄 Validation de en.json...");
  const enValidation = validateJSON(EN_FILE);

  if (!enValidation.valid) {
    console.error(`❌ Erreur de syntaxe JSON dans en.json: ${enValidation.error}`);
    return 1;
  }

  const enData = enValidation.data;
  const enDepth = getMaxDepth(enData);
  const enKeyCount = countKeys(enData);
  const enEmpty = findEmptyValues(enData);

  console.log(`   ✅ Syntaxe JSON valide`);
  console.log(`   📊 Profondeur maximale: ${enDepth}`);
  console.log(`   📊 Nombre de clés: ${enKeyCount}`);

  if (enEmpty.length > 0) {
    console.log(`   ⚠️  Valeurs vides détectées: ${enEmpty.length}`);
    enEmpty.forEach((key) => console.log(`      - ${key}`));
  }

  console.log("");

  // Comparer les structures
  console.log("🔍 Comparaison des structures...");

  if (frDepth !== enDepth) {
    console.log(`   ⚠️  Profondeurs différentes: FR=${frDepth}, EN=${enDepth}`);
  } else {
    console.log(`   ✅ Profondeurs identiques: ${frDepth}`);
  }

  if (frKeyCount !== enKeyCount) {
    console.log(`   ⚠️  Nombre de clés différent: FR=${frKeyCount}, EN=${enKeyCount}`);
  } else {
    console.log(`   ✅ Nombre de clés identique: ${frKeyCount}`);
  }

  console.log("");

  // Résumé
  const hasWarnings =
    frEmpty.length > 0 || enEmpty.length > 0 || frDepth !== enDepth || frKeyCount !== enKeyCount;

  if (!hasWarnings) {
    console.log("✅ Structure valide et cohérente !");
    return 0;
  } else {
    console.log("⚠️  Des avertissements ont été détectés. Veuillez les vérifier.");
    return 1;
  }
}

// Exécuter le script
if (require.main === module) {
  const exitCode = validateStructure();
  process.exit(exitCode);
}

module.exports = { validateStructure };
