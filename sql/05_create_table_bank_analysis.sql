-- Tabela: bank_analysis
-- Descrição: Armazena análises específicas de cada banco dentro de um período
-- Relacionamentos:
--   - N:1 com analysis (múltiplas análises de banco pertencem a uma análise)
--   - Referencia bank via bank_name (enum)

CREATE TABLE IF NOT EXISTS iedi.bank_analysis (
  id STRING(36) NOT NULL,
  analysis_id STRING(36) NOT NULL,
  bank_name STRING(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  total_mentions INT64 DEFAULT 0,
  positive_volume FLOAT64 DEFAULT 0.0,
  negative_volume FLOAT64 DEFAULT 0.0,
  iedi_mean FLOAT64,
  iedi_score FLOAT64
);

-- Comentários dos campos:
-- id: UUID da análise de banco
-- analysis_id: FK para analysis
-- bank_name: Nome do banco (enum BankName - ex: "BANCO_DO_BRASIL", "ITAU")
-- start_date: Data de início da análise para este banco
-- end_date: Data final da análise para este banco
-- total_mentions: Total de mentions processadas para este banco
-- positive_volume: Volume de mentions positivas
-- negative_volume: Volume de mentions negativas
-- iedi_mean: IEDI médio calculado para este banco
-- iedi_score: IEDI score final para este banco
