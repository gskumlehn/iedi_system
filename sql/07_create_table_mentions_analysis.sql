-- Tabela: mention_analysis
-- Descrição: Armazena análise IEDI de cada mention por banco
-- Relacionamentos:
--   - 1:1 com mention (cada mention tem uma análise)
--   - Referencia bank via bank_name (enum)

CREATE TABLE IF NOT EXISTS iedi.mention_analysis (
  id STRING(36) NOT NULL,
  mention_id STRING(36) NOT NULL,
  bank_name STRING(255) NOT NULL,
  sentiment STRING(50),
  reach_group STRING(10),
  niche_vehicle BOOL,
  title_mentioned BOOL,
  subtitle_used BOOL,
  subtitle_mentioned BOOL,
  iedi_score FLOAT64,
  iedi_normalized FLOAT64,
  numerator INT64,
  denominator INT64
);

-- Comentários dos campos:
-- mention_analysis_id: ID único para cada análise de menção (PK)
-- mention_id: FK para mention
-- bank_name: Nome do banco (enum BankName - ex: "BANCO_DO_BRASIL", "ITAU")
-- sentiment: Sentimento da mention (enum Sentiment - "POSITIVE", "NEGATIVE", "NEUTRAL")
-- reach_group: Grupo de alcance do veículo (enum ReachGroup - "A", "B", "C", "D")
-- niche_vehicle: Se o veículo é de nicho
-- title_mentioned: Se o banco foi mencionado no título
-- subtitle_used: Se o subtítulo foi analisado (snippet != fullText)
-- subtitle_mentioned: Se o banco foi mencionado no subtítulo
-- iedi_score: Score IEDI calculado (0.0 a 1.0)
-- iedi_normalized: IEDI normalizado (0 a 10)
-- numerator: Numerador da fórmula IEDI
-- denominator: Denominador da fórmula IEDI
