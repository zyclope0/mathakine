#!/usr/bin/env node

/**
 * Script de vérification des traductions
 * Vérifie que toutes les clés FR existent en EN et vice versa
 * Vérifie la structure identique entre les deux fichiers
 */

const fs = require('fs');
const path = require('path');

const FR_FILE = path.join(__dirname, '../../messages/fr.json');
const EN_FILE = path.join(__dirname, '../../messages/en.json');

// Fonction pour obtenir toutes les clés d'un objet (récursif)
function getAllKeys(obj, prefix = '') {
  const keys = [];
  
  for (const key in obj) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    
    if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
      keys.push(...getAllKeys(obj[key], fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  
  return keys;
}

// Fonction pour obtenir la valeur d'une clé (avec chemin pointé)
function getValue(obj, keyPath) {
  const keys = keyPath.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key];
    } else {
      return undefined;
    }
  }
  
  return current;
}

// Fonction pour obtenir la structure d'un objet (sans valeurs)
function getStructure(obj) {
  const structure = {};
  
  for (const key in obj) {
    if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
      structure[key] = getStructure(obj[key]);
    } else {
      structure[key] = null; // Marqueur pour valeur feuille
    }
  }
  
  return structure;
}

// Fonction pour comparer deux structures
function compareStructures(struct1, struct2, prefix = '') {
  const differences = [];
  
  // Vérifier les clés manquantes dans struct2
  for (const key in struct1) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    
    if (!(key in struct2)) {
      differences.push({
        type: 'missing_in_en',
        key: fullKey,
        message: `Clé manquante dans en.json: ${fullKey}`
      });
    } else if (struct1[key] === null && struct2[key] !== null) {
      // struct1 a une valeur feuille mais struct2 a un objet
      differences.push({
        type: 'structure_mismatch',
        key: fullKey,
        message: `Structure différente: ${fullKey} est une valeur dans fr.json mais un objet dans en.json`
      });
    } else if (struct1[key] !== null && struct2[key] === null) {
      // struct1 a un objet mais struct2 a une valeur feuille
      differences.push({
        type: 'structure_mismatch',
        key: fullKey,
        message: `Structure différente: ${fullKey} est un objet dans fr.json mais une valeur dans en.json`
      });
    } else if (struct1[key] !== null && struct2[key] !== null) {
      // Les deux sont des objets, comparer récursivement
      differences.push(...compareStructures(struct1[key], struct2[key], fullKey));
    }
  }
  
  // Vérifier les clés supplémentaires dans struct2
  for (const key in struct2) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    
    if (!(key in struct1)) {
      differences.push({
        type: 'missing_in_fr',
        key: fullKey,
        message: `Clé manquante dans fr.json: ${fullKey}`
      });
    }
  }
  
  return differences;
}

// Fonction principale
function checkTranslations() {
  console.log('🔍 Vérification des traductions...\n');
  
  // Lire les fichiers
  let frMessages, enMessages;
  
  try {
    frMessages = JSON.parse(fs.readFileSync(FR_FILE, 'utf8'));
  } catch (error) {
    console.error('❌ Erreur lors de la lecture de fr.json:', error.message);
    process.exit(1);
  }
  
  try {
    enMessages = JSON.parse(fs.readFileSync(EN_FILE, 'utf8'));
  } catch (error) {
    console.error('❌ Erreur lors de la lecture de en.json:', error.message);
    process.exit(1);
  }
  
  // Obtenir toutes les clés
  const frKeys = getAllKeys(frMessages);
  const enKeys = getAllKeys(enMessages);
  
  console.log(`📊 Statistiques:`);
  console.log(`   - Clés FR: ${frKeys.length}`);
  console.log(`   - Clés EN: ${enKeys.length}\n`);
  
  // Vérifier les clés manquantes
  const missingInEn = frKeys.filter(key => !enKeys.includes(key));
  const missingInFr = enKeys.filter(key => !frKeys.includes(key));
  
  // Vérifier la structure
  const frStructure = getStructure(frMessages);
  const enStructure = getStructure(enMessages);
  const structureDifferences = compareStructures(frStructure, enStructure);
  
  // Afficher les résultats
  let hasErrors = false;
  
  if (missingInEn.length > 0) {
    hasErrors = true;
    console.log('❌ Clés manquantes dans en.json:');
    missingInEn.forEach(key => console.log(`   - ${key}`));
    console.log('');
  }
  
  if (missingInFr.length > 0) {
    hasErrors = true;
    console.log('❌ Clés manquantes dans fr.json:');
    missingInFr.forEach(key => console.log(`   - ${key}`));
    console.log('');
  }
  
  if (structureDifferences.length > 0) {
    hasErrors = true;
    console.log('❌ Différences de structure:');
    structureDifferences.forEach(diff => console.log(`   - ${diff.message}`));
    console.log('');
  }
  
  if (!hasErrors) {
    console.log('✅ Toutes les traductions sont cohérentes !');
    console.log(`   - ${frKeys.length} clés vérifiées`);
    console.log(`   - Structure identique entre FR et EN`);
    return 0;
  } else {
    console.log('❌ Des problèmes ont été détectés. Veuillez les corriger.');
    return 1;
  }
}

// Exécuter le script
if (require.main === module) {
  const exitCode = checkTranslations();
  process.exit(exitCode);
}

module.exports = { checkTranslations };

