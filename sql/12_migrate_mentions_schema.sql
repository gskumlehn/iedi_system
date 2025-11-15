-- Migration script: Refactor mentions schema
-- Remove analysis_id from mentions and create analysis_mentions relationship table

-- Step 1: Create new analysis_mentions table (if not exists)
CREATE TABLE IF NOT EXISTS iedi.analysis_mentions (
  analysis_id INT64 NOT NULL,
  mention_id INT64 NOT NULL,
  bank_id INT64 NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Step 2: Migrate data from old mentions to analysis_mentions
-- Extract bank_id from categories array (assuming first category is the bank)
INSERT INTO iedi.analysis_mentions (analysis_id, mention_id, bank_id, created_at)
SELECT 
  m.analysis_id,
  m.id AS mention_id,
  b.id AS bank_id,
  m.created_at
FROM iedi.mentions m
CROSS JOIN UNNEST(m.categories) AS category_name
JOIN iedi.banks b ON b.name = category_name
WHERE m.analysis_id IS NOT NULL;

-- Step 3: Create backup of old mentions table
CREATE TABLE IF NOT EXISTS iedi.mentions_backup AS
SELECT * FROM iedi.mentions;

-- Step 4: Create new mentions table without analysis_id
CREATE TABLE IF NOT EXISTS iedi.mentions_new (
  id INT64 NOT NULL,
  brandwatch_id STRING NOT NULL,
  categories ARRAY<STRING>,
  title STRING,
  snippet STRING,
  full_text STRING,
  url STRING,
  domain STRING,
  published_date TIMESTAMP,
  sentiment STRING NOT NULL,
  monthly_visitors INT64,
  reach_group STRING,
  title_verified BOOL DEFAULT FALSE,
  subtitle_verified BOOL DEFAULT FALSE,
  relevant_outlet_verified BOOL DEFAULT FALSE,
  niche_outlet_verified BOOL DEFAULT FALSE,
  numerator FLOAT64 DEFAULT 0.0,
  denominator FLOAT64 DEFAULT 0.0,
  score FLOAT64 DEFAULT 0.0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Step 5: Migrate data to new table (removing duplicates by brandwatch_id)
INSERT INTO iedi.mentions_new
SELECT DISTINCT
  id,
  brandwatch_id,
  categories,
  title,
  snippet,
  full_text,
  url,
  domain,
  published_date,
  sentiment,
  monthly_visitors,
  reach_group,
  title_verified,
  subtitle_verified,
  relevant_outlet_verified,
  niche_outlet_verified,
  numerator,
  denominator,
  score,
  created_at
FROM iedi.mentions
WHERE brandwatch_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY brandwatch_id ORDER BY created_at DESC) = 1;

-- Step 6: Drop old table and rename new one
-- MANUAL STEP: After validating data, run:
-- DROP TABLE iedi.mentions;
-- ALTER TABLE iedi.mentions_new RENAME TO mentions;

-- Validation queries:
-- SELECT COUNT(*) FROM iedi.mentions_backup;
-- SELECT COUNT(DISTINCT brandwatch_id) FROM iedi.mentions_new;
-- SELECT COUNT(*) FROM iedi.analysis_mentions;
