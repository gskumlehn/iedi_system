CREATE TABLE IF NOT EXISTS iedi.mention_analysis (
  mention_id STRING(36) NOT NULL,
  bank_name STRING(255) NOT NULL,
  iedi_score FLOAT64,
  iedi_normalized FLOAT64,
  numerator INT64,
  denominator INT64,
  created_at TIMESTAMP NOT NULL
);
