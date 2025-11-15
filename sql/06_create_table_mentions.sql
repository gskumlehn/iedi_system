-- Tabela de Menções - Dados Brutos da Brandwatch API
-- 
-- Esta tabela armazena menções ÚNICAS identificadas por brandwatch_id.
-- Contém APENAS dados brutos (não processados) da API Brandwatch.
-- 
-- Cálculos IEDI específicos por banco são armazenados em analysis_mentions.
-- Uma menção pode citar múltiplos bancos, cada um com seu próprio cálculo IEDI.

CREATE TABLE IF NOT EXISTS iedi.mentions (
  -- Identificadores
  id STRING(36) NOT NULL,
  brandwatch_id STRING(255),
  
  -- Dados brutos da Brandwatch (não processados)
  categories ARRAY<STRING>,           -- Lista de bancos detectados (raw)
  sentiment STRING(50) NOT NULL,      -- Sentimento: positive, negative, neutral
  title STRING,                       -- Título da menção
  snippet STRING,                     -- Trecho/resumo
  full_text STRING,                   -- Texto completo
  url STRING(500),                    -- URL da menção
  domain STRING(255),                 -- Domínio do veículo
  published_date TIMESTAMP,           -- Data de publicação
  
  -- Metadados do veículo de mídia
  media_outlet_id STRING(36),         -- FK para media_outlets
  monthly_visitors INT64 DEFAULT 0,   -- Visitantes mensais do veículo
  reach_group STRING(10) NOT NULL,    -- Grupo de alcance: A, B, C, D
  
  -- Timestamps de auditoria
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP,
  
  PRIMARY KEY (id)
);

-- Índice para busca por brandwatch_id (identificador único da Brandwatch)
CREATE UNIQUE INDEX IF NOT EXISTS idx_mentions_brandwatch_id 
ON iedi.mentions(brandwatch_id);

-- Índice para busca por domínio
CREATE INDEX IF NOT EXISTS idx_mentions_domain 
ON iedi.mentions(domain);

-- Índice para busca por data de publicação
CREATE INDEX IF NOT EXISTS idx_mentions_published_date 
ON iedi.mentions(published_date);

-- Índice para busca por veículo de mídia
CREATE INDEX IF NOT EXISTS idx_mentions_media_outlet_id 
ON iedi.mentions(media_outlet_id);
