CREATE TABLE IF NOT EXISTS iedi.bank_analysis (
  id STRING(36) NOT NULL,
  analysis_id STRING(36) NOT NULL,
  bank_name STRING(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  positive_volume INT64,
  negative_volume INT64,
  created_at TIMESTAMP NOT NULL
);
