CREATE TABLE IF NOT EXISTS iedi.analyses (
  id INT64 NOT NULL,
  name STRING(255) NOT NULL,
  query_name STRING(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  custom_period BOOL NOT NULL DEFAULT FALSE,
  status STRING(50) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'Analyses - IEDI analysis metadata'
);
