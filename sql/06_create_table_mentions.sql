CREATE TABLE IF NOT EXISTS iedi.mentions (
  id STRING(36) NOT NULL,
  url STRING(500) NOT NULL,
  brandwatch_id STRING(255),
  original_url STRING(500),
  categories ARRAY<STRING>,
  sentiment STRING(50) NOT NULL,
  title STRING,
  snippet STRING,
  full_text STRING,
  domain STRING(255),
  published_date TIMESTAMP,
  media_outlet_id STRING(36),
  monthly_visitors INT64,
  reach_group STRING(10) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP
);
