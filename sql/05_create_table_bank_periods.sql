-- Tabela: bank_period
-- Descrição: Armazena períodos específicos de cada banco dentro de uma análise
-- Relacionamentos:
--   - N:1 com analysis (múltiplos períodos pertencem a uma análise)
--   - N:1 com bank (múltiplos períodos podem referenciar o mesmo banco)

CREATE TABLE IF NOT EXISTS iedi.bank_period (
  id STRING(36) NOT NULL,
  analysis_id STRING(36) NOT NULL,
  bank_id STRING(36) NOT NULL,
  category_detail STRING(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  total_mentions INT64 NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Comentários dos campos:
-- id: UUID do período
-- analysis_id: FK para analysis
-- bank_id: FK para bank
-- category_detail: Nome da categoria na Brandwatch (usado para filtrar mentions)
-- start_date: Data de início específica deste banco
-- end_date: Data final específica deste banco
-- total_mentions: Total de mentions processadas para este banco
-- created_at: Data de criação do registro
