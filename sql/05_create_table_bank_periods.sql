CREATE TABLE IF NOT EXISTS iedi.bank_periods (
  id STRING(36) NOT NULL,
  analysis_id STRING(36) NOT NULL,
  bank_id STRING(36) NOT NULL,
  category_detail STRING(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL
);
