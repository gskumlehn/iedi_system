-- Tabela de Relacionamento Análise-Menção-Banco + Cálculos IEDI
-- 
-- Esta tabela conecta análises, menções e bancos, armazenando os cálculos IEDI
-- específicos para cada combinação (análise + menção + banco).
-- 
-- Uma menção pode citar múltiplos bancos. Cada banco terá seu próprio registro
-- com cálculos IEDI independentes.
-- 
-- Exemplo:
--   Menção: "BB e Itaú anunciam parceria"
--   Registros:
--     - (analysis_1, mention_1, banco_bb, iedi_score=85.5)
--     - (analysis_1, mention_1, banco_itau, iedi_score=82.3)

CREATE TABLE IF NOT EXISTS iedi.analysis_mentions (
  -- Chave primária composta (análise + menção + banco)
  analysis_id STRING(36) NOT NULL,
  mention_id STRING(36) NOT NULL,
  bank_id STRING(36) NOT NULL,
  
  -- Cálculos IEDI específicos para este banco nesta análise
  iedi_score FLOAT64,                 -- Score IEDI final (0-100)
  iedi_normalized FLOAT64,            -- Score normalizado (0-1)
  numerator INT64,                    -- Numerador da fórmula IEDI
  denominator INT64,                  -- Denominador da fórmula IEDI
  
  -- Flags de verificação (específicas por banco)
  title_verified INT64 DEFAULT 0,    -- Banco mencionado no título (0 ou 1)
  subtitle_verified INT64 DEFAULT 0, -- Banco mencionado no subtítulo (0 ou 1)
  relevant_outlet_verified INT64 DEFAULT 0,  -- Veículo relevante (0 ou 1)
  niche_outlet_verified INT64 DEFAULT 0,     -- Veículo de nicho (0 ou 1)
  
  -- Timestamp de criação do relacionamento
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  
  PRIMARY KEY (analysis_id, mention_id, bank_id),
  
  -- Foreign keys
  FOREIGN KEY (analysis_id) REFERENCES iedi.analyses(id),
  FOREIGN KEY (mention_id) REFERENCES iedi.mentions(id),
  FOREIGN KEY (bank_id) REFERENCES iedi.banks(id)
);

-- Índice para busca por análise
CREATE INDEX IF NOT EXISTS idx_analysis_mentions_analysis_id 
ON iedi.analysis_mentions(analysis_id);

-- Índice para busca por menção
CREATE INDEX IF NOT EXISTS idx_analysis_mentions_mention_id 
ON iedi.analysis_mentions(mention_id);

-- Índice para busca por banco
CREATE INDEX IF NOT EXISTS idx_analysis_mentions_bank_id 
ON iedi.analysis_mentions(bank_id);

-- Índice composto para busca por análise + banco
CREATE INDEX IF NOT EXISTS idx_analysis_mentions_analysis_bank 
ON iedi.analysis_mentions(analysis_id, bank_id);

-- Índice para ordenação por score IEDI
CREATE INDEX IF NOT EXISTS idx_analysis_mentions_iedi_score 
ON iedi.analysis_mentions(iedi_score DESC);
