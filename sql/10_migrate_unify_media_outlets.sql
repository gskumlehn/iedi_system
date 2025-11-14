-- Unify relevant_media_outlets and niche_media_outlets into single table

-- 1. Create unified media_outlets table
CREATE TABLE IF NOT EXISTS iedi.media_outlets (
  id INT64 NOT NULL,
  name STRING(255) NOT NULL,
  domain STRING(255) NOT NULL,
  category STRING(100),
  monthly_visitors INT64,
  is_niche BOOL NOT NULL DEFAULT FALSE,
  active BOOL NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'Media outlets - unified table for relevant and niche press vehicles'
);

-- 2. Migrate data from relevant_media_outlets (is_niche = FALSE)
INSERT INTO iedi.media_outlets (id, name, domain, category, monthly_visitors, is_niche, active, created_at, updated_at)
SELECT 
  id,
  name,
  domain,
  category,
  NULL as monthly_visitors,  -- Relevant outlets don't have this field
  FALSE as is_niche,
  active,
  created_at,
  updated_at
FROM iedi.relevant_media_outlets;

-- 3. Migrate data from niche_media_outlets (is_niche = TRUE)
INSERT INTO iedi.media_outlets (id, name, domain, category, monthly_visitors, is_niche, active, created_at, updated_at)
SELECT 
  id + 1000 as id,  -- Offset IDs to avoid conflicts
  name,
  domain,
  category,
  monthly_visitors,
  TRUE as is_niche,
  active,
  created_at,
  updated_at
FROM iedi.niche_media_outlets;

-- 4. Drop old tables (uncomment after verifying migration)
-- DROP TABLE IF EXISTS iedi.relevant_media_outlets;
-- DROP TABLE IF EXISTS iedi.niche_media_outlets;
