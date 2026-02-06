-- Migration: Ajouter les groupes d'âge manquants à l'ENUM agegroup
-- Date: 2026-02-03
-- Description: Ajoute GROUP_6_8, GROUP_15_17, et ADULT à l'ENUM PostgreSQL
--
-- AVANT d'exécuter:
-- 1. Faire un backup de la base de données
-- 2. Vérifier les ENUMs existants avec: SELECT enumlabel FROM pg_enum WHERE enumtypid = 'agegroup'::regtype;
--
-- NOTE: ALTER TYPE ADD VALUE ne peut pas être exécuté dans une transaction,
-- donc chaque commande doit être exécutée séparément.

-- Vérifier les valeurs actuelles (pour information)
-- SELECT enumlabel FROM pg_enum WHERE enumtypid = 'agegroup'::regtype ORDER BY enumsortorder;

-- Ajouter GROUP_6_8 (pour les 6-8 ans)
ALTER TYPE agegroup ADD VALUE IF NOT EXISTS 'GROUP_6_8';

-- Ajouter GROUP_15_17 (pour les 15-17 ans)
ALTER TYPE agegroup ADD VALUE IF NOT EXISTS 'GROUP_15_17';

-- Ajouter ADULT (pour les adultes)
ALTER TYPE agegroup ADD VALUE IF NOT EXISTS 'ADULT';

-- Vérification après migration
-- SELECT enumlabel FROM pg_enum WHERE enumtypid = 'agegroup'::regtype ORDER BY enumsortorder;

-- Résultat attendu:
-- GROUP_10_12 (existant - pour 9-11 ans)
-- GROUP_13_15 (existant - pour 12-14 ans)
-- ALL_AGES    (existant - tous âges)
-- GROUP_6_8   (nouveau - pour 6-8 ans)
-- GROUP_15_17 (nouveau - pour 15-17 ans)
-- ADULT       (nouveau - pour adultes)
