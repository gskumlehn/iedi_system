CREATE TABLE IF NOT EXISTS iedi.iedi_results (
  id STRING(36) NOT NULL,
  analysis_id STRING(36) NOT NULL,
  bank_id STRING(36) NOT NULL,
  total_mentions INT64 NOT NULL,
  final_iedi FLOAT64 NOT NULL,
  created_at TIMESTAMP NOT NULL
);
