CREATE TABLE IF NOT EXISTS iedi.mentions (
  id INT64 NOT NULL,
  analysis_id INT64 NOT NULL,
  categories ARRAY<STRING> NOT NULL,
  brandwatch_id STRING(255) NOT NULL,
  title STRING,
  snippet STRING,
  full_text STRING,
  url STRING,
  domain STRING(255),
  published_date TIMESTAMP,
  sentiment STRING(50) NOT NULL,
  monthly_visitors INT64,
  reach_group STRING(10),
  title_verified BOOL DEFAULT FALSE,
  subtitle_verified BOOL DEFAULT FALSE,
  relevant_outlet_verified BOOL DEFAULT FALSE,
  niche_outlet_verified BOOL DEFAULT FALSE,
  numerator FLOAT64 DEFAULT 0.0,
  denominator FLOAT64 DEFAULT 0.0,
  score FLOAT64 DEFAULT 0.0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'Mentions - individual press mentions from Brandwatch'
);
