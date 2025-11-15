CREATE TABLE IF NOT EXISTS iedi.analysis_mentions (
  analysis_id STRING NOT NULL,
  mention_id STRING NOT NULL,
  bank_id STRING NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
