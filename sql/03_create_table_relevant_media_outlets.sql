CREATE TABLE IF NOT EXISTS iedi.relevant_media_outlets (
  id INT64 NOT NULL,
  name STRING(255) NOT NULL,
  domain STRING(255) NOT NULL,
  category STRING(100),
  active BOOL NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'Relevant media outlets - major press vehicles'
);
