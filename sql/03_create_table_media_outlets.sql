CREATE TABLE IF NOT EXISTS iedi.media_outlet (
  id STRING(36) NOT NULL,
  name STRING(255) NOT NULL,
  domain STRING(255) NOT NULL,
  monthly_visitors INT64,
  is_niche BOOL NOT NULL,
  active BOOL NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
