-- ============================================================================
-- SQL de Correção de Domains - Media Outlets
-- Objetivo: Atualizar subdomínios para domains raiz para matching com Brandwatch
-- ============================================================================

-- Backup da tabela original (recomendado)
-- CREATE TABLE iedi.media_outlets_backup AS SELECT * FROM iedi.media_outlets;

-- Corrigir: agenciabrasil.ebc.com.br -> ebc.com.br (23 mentions)
UPDATE iedi.media_outlets
SET domain = 'ebc.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'agenciabrasil.ebc.com.br';

-- Corrigir: band.uol.com.br -> uol.com.br (238 mentions)
UPDATE iedi.media_outlets
SET domain = 'uol.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'band.uol.com.br';

-- Corrigir: economia.uol.com.br -> uol.com.br (238 mentions)
UPDATE iedi.media_outlets
SET domain = 'uol.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'economia.uol.com.br';

-- Corrigir: einvestidor.estadao.com.br -> estadao.com.br (124 mentions)
UPDATE iedi.media_outlets
SET domain = 'estadao.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'einvestidor.estadao.com.br';

-- Corrigir: epocanegocios.globo.com -> globo.com (334 mentions)
UPDATE iedi.media_outlets
SET domain = 'globo.com',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'epocanegocios.globo.com';

-- Corrigir: exame.com/pme -> exame.com (44 mentions)
UPDATE iedi.media_outlets
SET domain = 'exame.com',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'exame.com/pme';

-- Corrigir: folha.uol.com.br -> uol.com.br (238 mentions)
UPDATE iedi.media_outlets
SET domain = 'uol.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'folha.uol.com.br';

-- Corrigir: g1.globo.com -> globo.com (334 mentions)
UPDATE iedi.media_outlets
SET domain = 'globo.com',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'g1.globo.com';

-- Corrigir: g1.globo.com/economia/agronegocios/globo-rural -> globo.com (334 mentions)
UPDATE iedi.media_outlets
SET domain = 'globo.com',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'g1.globo.com/economia/agronegocios/globo-rural';

-- Corrigir: g1.globo.com/globonews -> globo.com (334 mentions)
UPDATE iedi.media_outlets
SET domain = 'globo.com',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'g1.globo.com/globonews';

-- Corrigir: oglobo.globo.com -> globo.com (334 mentions)
UPDATE iedi.media_outlets
SET domain = 'globo.com',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'oglobo.globo.com';

-- Corrigir: pme.estadao.com.br -> estadao.com.br (124 mentions)
UPDATE iedi.media_outlets
SET domain = 'estadao.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'pme.estadao.com.br';

-- Corrigir: pro.infomoney.com.br -> infomoney.com.br (178 mentions)
UPDATE iedi.media_outlets
SET domain = 'infomoney.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'pro.infomoney.com.br';

-- Corrigir: valor.globo.com -> globo.com (334 mentions)
UPDATE iedi.media_outlets
SET domain = 'globo.com',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'valor.globo.com';

-- Corrigir: valorinveste.globo.com -> globo.com (334 mentions)
UPDATE iedi.media_outlets
SET domain = 'globo.com',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'valorinveste.globo.com';

-- Corrigir: veja.abril.com.br -> abril.com.br (27 mentions)
UPDATE iedi.media_outlets
SET domain = 'abril.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'veja.abril.com.br';

-- Corrigir: vocerh.abril.com.br -> abril.com.br (27 mentions)
UPDATE iedi.media_outlets
SET domain = 'abril.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'vocerh.abril.com.br';

-- Corrigir: vocesa.abril.com.br -> abril.com.br (27 mentions)
UPDATE iedi.media_outlets
SET domain = 'abril.com.br',
    updated_at = CURRENT_TIMESTAMP()
WHERE domain = 'vocesa.abril.com.br';


-- ============================================================================
-- Verificação Final
-- ============================================================================

-- Contar media_outlets atualizados
SELECT
  'Total de media_outlets' as metric,
  COUNT(*) as value
FROM iedi.media_outlets
UNION ALL
SELECT
  'Veículos relevantes (is_niche=false)' as metric,
  COUNT(*) as value
FROM iedi.media_outlets
WHERE is_niche = false
UNION ALL
SELECT
  'Veículos de nicho (is_niche=true)' as metric,
  COUNT(*) as value
FROM iedi.media_outlets
WHERE is_niche = true;