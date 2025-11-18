-- Tabela: iedi_result
-- Descrição: Armazena resultados agregados de IEDI por banco em uma análise
-- Relacionamentos:
--   - N:1 com analysis (múltiplos resultados pertencem a uma análise)
--   - N:1 com bank (múltiplos resultados podem referenciar o mesmo banco)

CREATE TABLE IF NOT EXISTS iedi.iedi_result (
  id STRING(36) NOT NULL,
  analysis_id STRING(36) NOT NULL,
  bank_id STRING(36) NOT NULL,
  total_volume INT64 NOT NULL DEFAULT 0,
  positive_volume INT64 NOT NULL DEFAULT 0,
  negative_volume INT64 NOT NULL DEFAULT 0,
  neutral_volume INT64 NOT NULL DEFAULT 0,
  average_iedi FLOAT64 NOT NULL DEFAULT 0.0,
  final_iedi FLOAT64 NOT NULL DEFAULT 0.0,
  positivity_rate FLOAT64 NOT NULL DEFAULT 0.0,
  negativity_rate FLOAT64 NOT NULL DEFAULT 0.0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Comentários dos campos:
-- id: UUID do resultado
-- analysis_id: FK para analysis
-- bank_id: FK para bank
-- total_volume: Total de mentions (positivas + negativas + neutras)
-- positive_volume: Quantidade de mentions com sentimento positivo
-- negative_volume: Quantidade de mentions com sentimento negativo
-- neutral_volume: Quantidade de mentions com sentimento neutro
-- average_iedi: IEDI médio (média aritmética de todos os IEDI scores)
-- final_iedi: IEDI final (balizado pela proporção de mentions positivas)
--             Fórmula: average_iedi × (positive_volume / total_volume)
-- positivity_rate: Percentual de mentions positivas (0-100)
--                  Fórmula: (positive_volume / total_volume) × 100
-- negativity_rate: Percentual de mentions negativas (0-100)
--                  Fórmula: (negative_volume / total_volume) × 100
-- created_at: Data de criação do registro
