CREATE TABLE IF NOT EXISTS iedi.iedi_results (
  id STRING NOT NULL,
  analysis_id STRING NOT NULL,
  bank_id STRING NOT NULL,
  total_volume INT64 NOT NULL DEFAULT 0,
  positive_volume INT64 NOT NULL DEFAULT 0,
  negative_volume INT64 NOT NULL DEFAULT 0,
  neutral_volume INT64 NOT NULL DEFAULT 0,
  average_iedi FLOAT64 NOT NULL DEFAULT 0.0,
  final_iedi FLOAT64 NOT NULL DEFAULT 0.0,
  positivity_rate FLOAT64 NOT NULL DEFAULT 0.0,
  negativity_rate FLOAT64 NOT NULL DEFAULT 0.0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
