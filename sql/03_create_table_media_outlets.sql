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
  description = 'Media outlets - unified table for relevant and niche press vehicles. is_niche=FALSE for major outlets, is_niche=TRUE for specialized outlets'
);
