CREATE TABLE IF NOT EXISTS iedi.bank_periods (
  id INT64 NOT NULL,
  analysis_id INT64 NOT NULL,
  bank_id INT64 NOT NULL,
  category_detail STRING NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  total_mentions INT64 DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
