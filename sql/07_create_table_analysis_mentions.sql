CREATE TABLE IF NOT EXISTS iedi.analysis_mentions (
  analysis_id STRING(36) NOT NULL,
  mention_id STRING(36) NOT NULL,
  bank_id STRING(36) NOT NULL,
  iedi_score FLOAT64,
  iedi_normalized FLOAT64,
  numerator INT64,
  denominator INT64,
  title_verified INT64,
  subtitle_verified INT64,
  relevant_outlet_verified INT64,
  niche_outlet_verified INT64,
  created_at TIMESTAMP NOT NULL
);
