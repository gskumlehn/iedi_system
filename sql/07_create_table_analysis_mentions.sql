CREATE TABLE IF NOT EXISTS iedi.analysis_mentions (
  analysis_id INT64 NOT NULL,
  mention_id INT64 NOT NULL,
  bank_id INT64 NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
