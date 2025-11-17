CREATE TABLE IF NOT EXISTS iedi.analysis (
  id STRING(36) NOT NULL,
  name STRING(255) NOT NULL,
  query_name STRING(255) NOT NULL,
  is_custom_dates BOOL NOT NULL,
  created_at TIMESTAMP NOT NULL
);
