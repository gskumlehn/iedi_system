CREATE TABLE IF NOT EXISTS iedi.iedi_results (
  id INT64 NOT NULL,
  analysis_id INT64 NOT NULL,
  bank_id INT64 NOT NULL,
  total_volume INT64 NOT NULL DEFAULT 0,
  positive_volume INT64 NOT NULL DEFAULT 0,
  negative_volume INT64 NOT NULL DEFAULT 0,
  neutral_volume INT64 NOT NULL DEFAULT 0,
  average_iedi FLOAT64 NOT NULL DEFAULT 0.0,
  final_iedi FLOAT64 NOT NULL DEFAULT 0.0,
  positivity_rate FLOAT64 NOT NULL DEFAULT 0.0,
  negativity_rate FLOAT64 NOT NULL DEFAULT 0.0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'IEDI results - aggregated IEDI scores per bank per analysis'
);
