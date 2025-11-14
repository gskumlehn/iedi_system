# Brandwatch - Filtros por Domínio

## Visão Geral

O sistema IEDI monitora **apenas 62 veículos de mídia** cadastrados nas listas de veículos relevantes e de nicho. Para otimizar o download de menções da Brandwatch API, devemos aplicar filtros por domínio para baixar apenas menções desses veículos.

---

## Benefícios do Filtro por Domínio

| Benefício | Descrição |
|-----------|-----------|
| **Redução de Tráfego** | Não baixa menções de veículos irrelevantes |
| **Processamento Mais Rápido** | Menos dados para processar e armazenar |
| **Economia de API Calls** | Brandwatch cobra por volume de dados |
| **Precisão** | Garante que apenas veículos monitorados sejam analisados |

---

## Domínios Monitorados

### Veículos Relevantes (40 domínios)

| ID | Nome | Domínio |
|----|------|---------|
| 1 | Agência Brasil | `agenciabrasil.ebc.com.br` |
| 2 | Band | `band.uol.com.br` |
| 3 | BandNews | `bandnewstv.com.br` |
| 4 | BBC Brasil | `bbc.com/portuguese` |
| 5 | Bloomberg | `bloomberg.com.br` |
| 6 | Bloomberg Línea | `bloomberglinea.com.br` |
| 7 | Brasil 247 | `brasil247.com` |
| 8 | Carta Capital | `cartacapital.com.br` |
| 9 | CNN Brasil | `cnnbrasil.com.br` |
| 10 | Correio Braziliense | `correiobraziliense.com.br` |
| 11 | E-Investidor | `einvestidor.estadao.com.br` |
| 12 | Época Negócios | `epocanegocios.globo.com` |
| 13 | Estadão | `estadao.com.br` |
| 14 | Exame | `exame.com` |
| 15 | Folha de S. Paulo | `folha.uol.com.br` |
| 16 | Forbes Brasil | `forbes.com.br` |
| 17 | G1 | `g1.globo.com` |
| 18 | Globo News | `g1.globo.com/globonews` |
| 19 | Globo Rural | `g1.globo.com/economia/agronegocios/globo-rural` |
| 20 | Infomoney | `infomoney.com.br` |
| 21 | Isto É | `istoe.com.br` |
| 22 | Isto É Dinheiro | `istoedinheiro.com.br` |
| 23 | Jovem Pan | `jovempan.com.br` |
| 24 | Metrópoles | `metropoles.com` |
| 25 | Money Times | `moneytimes.com.br` |
| 26 | O Antagonista | `oantagonista.com` |
| 27 | O Estado de S. Paulo | `estadao.com.br` |
| 28 | O Globo | `oglobo.globo.com` |
| 29 | Poder360 | `poder360.com.br` |
| 30 | R7 | `r7.com` |
| 31 | Record News | `recordnews.com.br` |
| 32 | Reuters Brasil | `reuters.com/brazil` |
| 33 | SBT News | `sbtnews.com.br` |
| 34 | Terra | `terra.com.br` |
| 35 | UOL | `uol.com.br` |
| 36 | UOL Economia | `economia.uol.com.br` |
| 37 | Valor Econômico | `valor.globo.com` |
| 38 | Valor Investe | `valorinveste.globo.com` |
| 39 | Veja | `veja.abril.com.br` |
| 40 | Você S/A | `vocesa.abril.com.br` |

### Veículos de Nicho (22 domínios)

| ID | Nome | Domínio |
|----|------|---------|
| 1001 | Brazil Journal | `braziljournal.com` |
| 1002 | Broadcast | `broadcast.com.br` |
| 1003 | Canal Rural | `canalrural.com.br` |
| 1004 | Conjur | `conjur.com.br` |
| 1005 | Contábeis | `contabeis.com.br` |
| 1006 | Convergência Digital | `convergenciadigital.com.br` |
| 1007 | Diário do Comércio | `diariodocomercio.com.br` |
| 1008 | DCI | `dci.com.br` |
| 1009 | Estadão PME | `pme.estadao.com.br` |
| 1010 | Exame PME | `exame.com/pme` |
| 1011 | Gazeta do Povo | `gazetadopovo.com.br` |
| 1012 | InfoMoney Pro | `pro.infomoney.com.br` |
| 1013 | Jota | `jota.info` |
| 1014 | Mercado & Consumo | `mercadoeconsumo.com.br` |
| 1015 | Neofeed | `neofeed.com.br` |
| 1016 | Notícias Agrícolas | `noticiasagricolas.com.br` |
| 1017 | Pipeline | `pipeline.com.br` |
| 1018 | Seu Dinheiro | `seudinheiro.com` |
| 1019 | StartSe | `startse.com` |
| 1020 | Teletime | `teletime.com.br` |
| 1021 | The Brief | `thebrief.com.br` |
| 1022 | Você RH | `vocerh.abril.com.br` |

---

## Implementação na Brandwatch API

### Filtro por Domínio (site)

A Brandwatch API suporta filtro por domínio através do parâmetro `site`:

```bash
curl -X GET 'https://api.brandwatch.com/projects/PROJECT_ID/data/mentions?queryId=QUERY_ID&startDate=2024-01-01&endDate=2024-01-31&site=g1.globo.com&site=valor.globo.com&site=exame.com'
```

### Implementação com bcr-api (Python)

```python
from bcr_api import BrandwatchClient

client = BrandwatchClient()

# Lista de domínios monitorados
MONITORED_DOMAINS = [
    'agenciabrasil.ebc.com.br',
    'band.uol.com.br',
    'bandnewstv.com.br',
    # ... todos os 62 domínios
]

# Baixar menções filtradas por domínio
mentions = client.get_mentions(
    project_id=PROJECT_ID,
    query_id=QUERY_ID,
    start_date='2024-01-01',
    end_date='2024-01-31',
    site=MONITORED_DOMAINS  # Filtro por domínio
)
```

---

## Alternativa: Filtro por Category

Se os domínios já estiverem categorizados na Brandwatch (ex: "Veículos IEDI"), podemos usar filtro por categoria:

```python
# Opção 1: Filtro por domínio (mais preciso)
mentions = client.get_mentions(..., site=MONITORED_DOMAINS)

# Opção 2: Filtro por categoria (se configurado na Brandwatch)
mentions = client.get_mentions(..., category=IEDI_VEHICLES_CATEGORY_ID)
```

---

## Validação

Após baixar as menções com filtro, validar que:

1. ✅ Todos os domínios retornados estão na lista de 62 veículos
2. ✅ Nenhuma menção de veículo não monitorado foi baixada
3. ✅ Volume de dados é significativamente menor

```python
def validate_domains(mentions, monitored_domains):
    """Valida que todas as menções são de domínios monitorados"""
    invalid_domains = set()
    
    for mention in mentions:
        domain = extract_domain(mention['url'])
        if domain not in monitored_domains:
            invalid_domains.add(domain)
    
    if invalid_domains:
        print(f"⚠️ Domínios não monitorados encontrados: {invalid_domains}")
    else:
        print("✅ Todas as menções são de domínios monitorados")
```

---

## Manutenção

Quando adicionar/remover veículos da lista:

1. Atualizar tabela `media_outlets` no BigQuery
2. Atualizar lista `MONITORED_DOMAINS` no código
3. Reprocessar análises afetadas (se necessário)

---

## Referências

- [Brandwatch API - Site Filter](https://developers.brandwatch.com/docs/filters#site)
- [bcr-api Documentation](https://github.com/BrandwatchLtd/bcr-api)
- `sql/09_insert_media_outlets.sql` - Lista completa de veículos
