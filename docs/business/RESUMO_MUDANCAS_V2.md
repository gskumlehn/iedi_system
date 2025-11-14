# Resumo Executivo - IEDI v2.0

## Mudanças Implementadas

### ❌ Removido: Porta-vozes (Peso 20)

**Motivo**: Não há lista completa e atualizada de porta-vozes dos bancos.

**Impacto**:
- Denominador reduzido em 20 pontos
- Cálculo permanece proporcional
- Implementação simplificada

### ❌ Removido: Imagens (Peso 20)

**Motivo**: Não há sistema de reconhecimento de logotipos/marcas dos bancos em imagens.

**Impacto**:
- Denominador reduzido em 20 pontos
- Cálculo permanece proporcional
- Implementação simplificada

### ✏️ Modificado: Subtítulo (Peso 80)

**Mudança**: Verificação agora é **condicional** - apenas quando `snippet ≠ fullText`.

**Motivo**: 
- `snippet` é "trecho que melhor corresponde à query", não necessariamente o subtítulo
- Em paywalls, `snippet == fullText` (texto completo indisponível)
- Garante precisão da análise

**Lógica Implementada**:
```python
if snippet != fullText:
    # Temos texto completo
    primeiro_paragrafo = extrair_primeiro_paragrafo(fullText)
    if banco_mencionado_em(primeiro_paragrafo):
        numerador += 80
    denominador += 80  # Peso sempre conta
else:
    # Paywall - não verificar
    # Peso NÃO é adicionado ao denominador
    pass
```

**Impacto**:
- Denominador se ajusta automaticamente
- Mantém justiça comparativa
- Evita falsos positivos

---

## Novos Denominadores

| Grupo | v1.0 (sem sub) | v1.0 (com sub) | v2.0 (sem sub) | v2.0 (com sub) |
|-------|----------------|----------------|----------------|----------------|
| **A** | 406 | 486 | 286 | 366 |
| **B** | 460 | 540 | 334 | 414 |
| **C** | 399 | 479 | 273 | 353 |
| **D** | 395 | 475 | 269 | 349 |

**Redução**: -40 pontos (porta-vozes + imagens) em todos os casos.

---

## Variáveis Ativas v2.0

| Variável | Peso | Status |
|----------|------|--------|
| Qualificação | - | ✅ Ativo |
| Título | 100 | ✅ Ativo |
| Subtítulo | 80 | ✏️ Condicional |
| ~~Porta-voz~~ | ~~20~~ | ❌ Removido |
| ~~Imagem~~ | ~~20~~ | ❌ Removido |
| Veículo Relevante | 95 | ✅ Ativo |
| Veículo de Nicho | 54 | ✅ Ativo |
| Grupo de Alcance | 20-91 | ✅ Ativo |

---

## Documentação Atualizada

1. **METODOLOGIA_IEDI_V2.md** (16 KB)
   - Explicação completa do cálculo
   - Lógica condicional do subtítulo
   - Exemplos práticos
   - Comparação v1.0 vs v2.0

2. **MAPEAMENTO_BRANDWATCH_V2.md** (14 KB)
   - Mapeamento direto de campos
   - Código Python de implementação
   - Configuração da query Brandwatch
   - Campos removidos documentados

3. **RESUMO_MUDANCAS_V2.md** (este arquivo)
   - Resumo executivo das mudanças
   - Tabelas comparativas
   - Próximos passos

---

## Próximos Passos de Implementação

### 1. Atualizar Calculadora IEDI

Modificar `app_en/services/iedi_calculator.py`:

```python
def calculate_mention_iedi(mention: dict, bank: Bank, ...) -> dict:
    # Remover verificações de porta-voz e imagem
    # Implementar lógica condicional de subtítulo
    
    if mention["snippet"] != mention.get("fullText", mention["snippet"]):
        # Verificar subtítulo
        subtitle_verified = True
        subtitle_points = check_subtitle(...)
    else:
        # Não verificar
        subtitle_verified = False
        subtitle_points = 0
    
    # Ajustar denominador
    if subtitle_verified:
        denominator += 80
```

### 2. Atualizar Models

Remover tabelas/campos não utilizados:
- ❌ Tabela `spokespersons` (se existir)
- ✅ Manter tabela `mentions` com campos:
  - `snippet` (TEXT)
  - `full_text` (TEXT)
  - `subtitle_verified` (BOOLEAN)

### 3. Atualizar Testes

Criar testes para:
- Cálculo com `snippet == fullText` (paywall)
- Cálculo com `snippet ≠ fullText` (texto completo)
- Verificação de denominadores corretos
- Comparação v1.0 vs v2.0

### 4. Atualizar Frontend

Mensagens em português:
- "Subtítulo verificado" / "Subtítulo não disponível (paywall)"
- Tooltip explicando a lógica condicional
- Indicador visual de verificações realizadas

---

## Benefícios da v2.0

✅ **Implementação Imediata**: Não depende de dados externos (porta-vozes, reconhecimento de imagem)

✅ **Precisão Aumentada**: Subtítulo só é verificado quando temos certeza do texto

✅ **Justiça Comparativa**: Denominador se ajusta automaticamente

✅ **Simplicidade**: Menos variáveis = menos complexidade

✅ **Escalabilidade**: Fácil adicionar porta-vozes e imagens no futuro

---

## Roadmap Futuro

### v2.1 - Porta-vozes
- Criar lista completa de porta-vozes por banco
- Implementar verificação no `fullText`
- Adicionar peso 20 de volta

### v2.2 - Imagens
- Implementar sistema de reconhecimento de logotipos
- Integrar com API de visão computacional
- Adicionar peso 20 de volta

### v3.0 - Machine Learning
- Classificação automática de sentimento
- Detecção de contexto (positivo/negativo)
- Pesos dinâmicos baseados em performance histórica

---

**Desenvolvido por**: Manus AI  
**Data**: 13/11/2024  
**Versão**: 2.0
