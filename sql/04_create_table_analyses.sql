CREATE TABLE IF NOT EXISTS iedi.analysis (
  id STRING(36) NOT NULL,
  period_type STRING(50) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  query_name STRING(255) NOT NULL,
  created_at TIMESTAMP NOT NULL
);
