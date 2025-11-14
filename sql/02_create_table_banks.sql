CREATE TABLE IF NOT EXISTS iedi.banks (
  id INT64 NOT NULL,
  name STRING(255) NOT NULL,
  variations ARRAY<STRING>,
  active BOOL NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'Banks table - stores bank information and name variations'
);
