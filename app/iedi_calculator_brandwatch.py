"""
Calculadora IEDI - Adaptada para Dados da Brandwatch
Baseada nas fórmulas originais do Power BI

Este módulo implementa o cálculo do Índice de Exposição Digital na Imprensa (IEDI)
usando exclusivamente os campos disponíveis na API da Brandwatch.
"""

from typing import List, Dict, Optional
from datetime import datetime
import re


class IEDICalculatorBrandwatch:
    """
    Calculadora IEDI otimizada para dados da Brandwatch
    
    Implementa as fórmulas originais do Power BI, adaptadas para os campos
    disponíveis na API da Brandwatch.
    """
    
    # Pesos das variáveis (conforme Power BI)
    PESO_GRUPO_A = 91
    PESO_GRUPO_B = 85
    PESO_GRUPO_C = 24
    PESO_GRUPO_D = 20
    PESO_VEICULO_RELEVANTE = 95
    PESO_VEICULO_NICHO = 54
    PESO_TITULO = 100
    PESO_SUBTITULO = 80
    PESO_IMAGEM = 20
    PESO_PORTAVOZ = 20
    
    # Denominadores (conforme Power BI)
    DENOMINADOR_GRUPO_A = 406  # 91 + 95 + 100 + 80 + 20 + 20
    DENOMINADOR_NAO_GRUPO_A = 460  # 91 + 95 + 54 + 100 + 80 + 20 + 20
    
    # Faixas de alcance (monthly visitors)
    GRUPO_A_MIN = 29_000_001
    GRUPO_B_MIN = 11_000_001
    GRUPO_B_MAX = 29_000_000
    GRUPO_C_MIN = 500_000
    GRUPO_C_MAX = 11_000_000
    GRUPO_D_MAX = 499_999
    
    def __init__(self, veiculos_relevantes: List[str], veiculos_nicho: List[str], 
                 portavozes: Dict[str, List[str]]):
        """
        Inicializa a calculadora
        
        Args:
            veiculos_relevantes: Lista de domínios de veículos relevantes
            veiculos_nicho: Lista de domínios de veículos de nicho
            portavozes: Dicionário {banco_nome: [lista_de_portavozes]}
        """
        self.veiculos_relevantes = [v.lower() for v in veiculos_relevantes]
        self.veiculos_nicho = [v.lower() for v in veiculos_nicho]
        self.portavozes = {k: [p.lower() for p in v] for k, v in portavozes.items()}
    
    def classificar_grupo_alcance(self, monthly_visitors: int) -> str:
        """
        Classifica o veículo em grupo de alcance (A, B, C ou D)
        
        Args:
            monthly_visitors: Número de visitantes mensais
        
        Returns:
            'A', 'B', 'C' ou 'D'
        """
        if monthly_visitors >= self.GRUPO_A_MIN:
            return 'A'
        elif self.GRUPO_B_MIN <= monthly_visitors <= self.GRUPO_B_MAX:
            return 'B'
        elif self.GRUPO_C_MIN <= monthly_visitors <= self.GRUPO_C_MAX:
            return 'C'
        else:
            return 'D'
    
    def verificar_titulo(self, title: str, banco_nome: str, variacoes: List[str]) -> bool:
        """
        Verifica se o banco aparece no título
        
        Args:
            title: Título da menção
            banco_nome: Nome do banco
            variacoes: Lista de variações do nome do banco
        
        Returns:
            True se banco aparece no título
        """
        if not title:
            return False
        
        title_lower = title.lower()
        
        # Verificar nome principal
        if banco_nome.lower() in title_lower:
            return True
        
        # Verificar variações
        for variacao in variacoes:
            if variacao.lower() in title_lower:
                return True
        
        return False
    
    def verificar_subtitulo(self, snippet: str, banco_nome: str, variacoes: List[str]) -> bool:
        """
        Verifica se o banco aparece no subtítulo/snippet
        
        Args:
            snippet: Snippet/subtítulo da menção
            banco_nome: Nome do banco
            variacoes: Lista de variações do nome do banco
        
        Returns:
            True se banco aparece no snippet
        """
        if not snippet:
            return False
        
        snippet_lower = snippet.lower()
        
        # Verificar nome principal
        if banco_nome.lower() in snippet_lower:
            return True
        
        # Verificar variações
        for variacao in variacoes:
            if variacao.lower() in snippet_lower:
                return True
        
        return False
    
    def verificar_imagem(self, image_urls: List[str]) -> bool:
        """
        Verifica se a menção possui imagem
        
        Args:
            image_urls: Lista de URLs de imagens
        
        Returns:
            True se possui imagem
        """
        return bool(image_urls and len(image_urls) > 0)
    
    def verificar_portavoz(self, full_text: str, banco_nome: str) -> bool:
        """
        Verifica se algum porta-voz do banco é mencionado
        
        Args:
            full_text: Texto completo da menção
            banco_nome: Nome do banco
        
        Returns:
            True se porta-voz é mencionado
        """
        if not full_text or banco_nome not in self.portavozes:
            return False
        
        full_text_lower = full_text.lower()
        
        for portavoz in self.portavozes[banco_nome]:
            if portavoz in full_text_lower:
                return True
        
        return False
    
    def verificar_veiculo_nicho(self, domain: str) -> bool:
        """
        Verifica se o veículo é de nicho
        
        Args:
            domain: Domínio do veículo
        
        Returns:
            True se é veículo de nicho
        """
        if not domain:
            return False
        
        domain_lower = domain.lower()
        
        for nicho in self.veiculos_nicho:
            if nicho in domain_lower:
                return True
        
        return False
    
    def calcular_iedi_mencao(self, mencao: Dict, banco_nome: str, variacoes: List[str]) -> Dict:
        """
        Calcula o IEDI de uma menção individual
        
        Args:
            mencao: Dicionário com dados da menção da Brandwatch
            banco_nome: Nome do banco
            variacoes: Lista de variações do nome do banco
        
        Returns:
            Dicionário com resultado do cálculo
        """
        # Extrair campos da Brandwatch
        sentiment = mencao.get('sentiment', 'neutral')
        title = mencao.get('title', '')
        snippet = mencao.get('snippet', '')
        full_text = mencao.get('fullText', '')
        image_urls = mencao.get('imageUrls', [])
        domain = mencao.get('domain', '')
        monthly_visitors = mencao.get('monthlyVisitors', 0)
        
        # 1. Verificações binárias
        verificacao_qualificacao = 1 if sentiment == 'positive' else 0
        verificacao_titulo = 1 if self.verificar_titulo(title, banco_nome, variacoes) else 0
        verificacao_subtitulo = 1 if self.verificar_subtitulo(snippet, banco_nome, variacoes) else 0
        verificacao_imagem = 1 if self.verificar_imagem(image_urls) else 0
        verificacao_portavoz = 1 if self.verificar_portavoz(full_text, banco_nome) else 0
        verificacao_veiculo_nicho = 1 if self.verificar_veiculo_nicho(domain) else 0
        
        # 2. Classificação de grupo
        grupo = self.classificar_grupo_alcance(monthly_visitors)
        grupo_a = 1 if grupo == 'A' else 0
        grupo_b = 1 if grupo == 'B' else 0
        grupo_c = 1 if grupo == 'C' else 0
        grupo_d = 1 if grupo == 'D' else 0
        
        # 3. Calcular numerador (sempre o mesmo)
        numerador = (
            (grupo_d * self.PESO_GRUPO_D) +
            (grupo_c * self.PESO_GRUPO_C) +
            (grupo_b * self.PESO_GRUPO_B) +
            (grupo_a * self.PESO_GRUPO_A) +
            (1 * self.PESO_VEICULO_RELEVANTE) +  # Sempre 1 (filtramos apenas relevantes)
            (verificacao_veiculo_nicho * self.PESO_VEICULO_NICHO) +
            (verificacao_titulo * self.PESO_TITULO) +
            (verificacao_subtitulo * self.PESO_SUBTITULO) +
            (verificacao_imagem * self.PESO_IMAGEM) +
            (verificacao_portavoz * self.PESO_PORTAVOZ)
        )
        
        # 4. Escolher denominador baseado no grupo
        denominador = self.DENOMINADOR_GRUPO_A if grupo_a == 1 else self.DENOMINADOR_NAO_GRUPO_A
        
        # 5. Calcular IEDI base
        iedi_base = numerador / denominador
        
        # 6. Aplicar sinal (positivo ou negativo)
        if verificacao_qualificacao == 0:  # Negativa
            iedi_base = iedi_base * -1
        
        # 7. Converter para escala 0-10
        iedi_0_a_10 = (10 * (iedi_base + 1)) / 2
        
        # 8. Limitar ao range 0-10
        iedi_0_a_10 = max(0, min(10, iedi_0_a_10))
        
        return {
            'iedi_-1_a_1': iedi_base,
            'iedi_0_a_10': iedi_0_a_10,
            'sentiment': 'positiva' if verificacao_qualificacao == 1 else 'negativa',
            'grupo_alcance': grupo,
            'variaveis': {
                'titulo': verificacao_titulo,
                'subtitulo': verificacao_subtitulo,
                'imagem': verificacao_imagem,
                'portavoz': verificacao_portavoz,
                'veiculo_nicho': verificacao_veiculo_nicho,
                'grupo': grupo,
                'monthly_visitors': monthly_visitors
            },
            'pesos_aplicados': {
                'numerador': numerador,
                'denominador': denominador
            }
        }
    
    def calcular_iedi_banco(self, mencoes: List[Dict], banco_nome: str, 
                           variacoes: List[str]) -> Dict:
        """
        Calcula o IEDI agregado de um banco
        
        Args:
            mencoes: Lista de menções do banco
            banco_nome: Nome do banco
            variacoes: Lista de variações do nome do banco
        
        Returns:
            Dicionário com resultado agregado
        """
        if not mencoes or len(mencoes) == 0:
            return {
                'banco': banco_nome,
                'iedi_medio': 0,
                'iedi_final': 0,
                'volume_total': 0,
                'volume_positivo': 0,
                'volume_negativo': 0,
                'positividade': 0,
                'negatividade': 0,
                'mencoes_detalhadas': []
            }
        
        # Calcular IEDI de cada menção
        resultados_mencoes = []
        soma_iedi = 0
        volume_positivo = 0
        volume_negativo = 0
        
        for mencao in mencoes:
            resultado = self.calcular_iedi_mencao(mencao, banco_nome, variacoes)
            
            # Adicionar dados da menção ao resultado
            resultado_completo = {
                **resultado,
                'mention_id': mencao.get('id'),
                'titulo': mencao.get('title'),
                'snippet': mencao.get('snippet'),
                'url': mencao.get('url'),
                'domain': mencao.get('domain'),
                'data_mencao': mencao.get('date'),
                'category_detail': mencao.get('categoryDetail')
            }
            
            resultados_mencoes.append(resultado_completo)
            soma_iedi += resultado['iedi_0_a_10']
            
            if resultado['sentiment'] == 'positiva':
                volume_positivo += 1
            else:
                volume_negativo += 1
        
        # Calcular métricas agregadas
        volume_total = len(mencoes)
        iedi_medio = soma_iedi / volume_total
        positividade = (volume_positivo / volume_total) * 100
        negatividade = (volume_negativo / volume_total) * 100
        
        # Aplicar balizamento (proporção de positivas)
        # Quanto maior a positividade, maior o IEDI final
        fator_balizamento = positividade / 100
        iedi_final = iedi_medio * fator_balizamento
        
        return {
            'banco': banco_nome,
            'iedi_medio': round(iedi_medio, 2),
            'iedi_final': round(iedi_final, 2),
            'volume_total': volume_total,
            'volume_positivo': volume_positivo,
            'volume_negativo': volume_negativo,
            'positividade': round(positividade, 2),
            'negatividade': round(negatividade, 2),
            'mencoes_detalhadas': resultados_mencoes
        }
    
    def calcular_iedi_comparativo(self, resultados_bancos: List[Dict]) -> List[Dict]:
        """
        Gera ranking comparativo de bancos
        
        Args:
            resultados_bancos: Lista de resultados de cada banco
        
        Returns:
            Lista ordenada por IEDI final (decrescente)
        """
        # Ordenar por IEDI final
        ranking = sorted(resultados_bancos, key=lambda x: x['iedi_final'], reverse=True)
        
        # Adicionar posição
        for i, resultado in enumerate(ranking):
            resultado['posicao'] = i + 1
        
        return ranking
    
    @staticmethod
    def calcular_indicadores_adicionais(mencoes: List[Dict], banco_nome: str) -> Dict:
        """
        Calcula indicadores complementares
        
        Args:
            mencoes: Lista de menções
            banco_nome: Nome do banco
        
        Returns:
            Dicionário com indicadores adicionais
        """
        if not mencoes:
            return {
                'presenca_positiva_titulos': 0,
                'presenca_positiva_titulos_perc': 0,
                'diversidade_veiculos': 0,
                'diversidade_grupo_a': 0,
                'diversidade_grupo_b': 0,
                'diversidade_grupo_c': 0,
                'diversidade_grupo_d': 0
            }
        
        # Filtrar menções positivas
        mencoes_positivas = [m for m in mencoes if m.get('sentiment') == 'positive']
        
        # Presença em títulos
        presenca_titulos = sum(1 for m in mencoes_positivas 
                              if banco_nome.lower() in m.get('title', '').lower())
        presenca_titulos_perc = (presenca_titulos / len(mencoes_positivas) * 100) if mencoes_positivas else 0
        
        # Diversidade de veículos
        dominios_positivos = set(m.get('domain') for m in mencoes_positivas if m.get('domain'))
        diversidade_total = len(dominios_positivos)
        
        # Diversidade por grupo
        calc = IEDICalculatorBrandwatch([], [], {})
        dominios_por_grupo = {'A': set(), 'B': set(), 'C': set(), 'D': set()}
        
        for mencao in mencoes_positivas:
            domain = mencao.get('domain')
            monthly_visitors = mencao.get('monthlyVisitors', 0)
            
            if domain:
                grupo = calc.classificar_grupo_alcance(monthly_visitors)
                dominios_por_grupo[grupo].add(domain)
        
        return {
            'presenca_positiva_titulos': presenca_titulos,
            'presenca_positiva_titulos_perc': round(presenca_titulos_perc, 2),
            'diversidade_veiculos': diversidade_total,
            'diversidade_grupo_a': len(dominios_por_grupo['A']),
            'diversidade_grupo_b': len(dominios_por_grupo['B']),
            'diversidade_grupo_c': len(dominios_por_grupo['C']),
            'diversidade_grupo_d': len(dominios_por_grupo['D'])
        }


def criar_calculadora_brandwatch(db) -> IEDICalculatorBrandwatch:
    """
    Factory para criar calculadora a partir do banco de dados
    
    Args:
        db: Instância do Database
    
    Returns:
        IEDICalculatorBrandwatch configurada
    """
    # Buscar veículos relevantes
    veiculos_relevantes = db.get_veiculos(tipo='relevante', ativo_only=True)
    dominios_relevantes = [v['domain'] for v in veiculos_relevantes if v.get('domain')]
    
    # Buscar veículos de nicho
    veiculos_nicho = db.get_veiculos(tipo='nicho', ativo_only=True)
    dominios_nicho = [v['domain'] for v in veiculos_nicho if v.get('domain')]
    
    # Buscar porta-vozes por banco
    bancos = db.get_bancos(ativo_only=True)
    portavozes_dict = {}
    
    for banco in bancos:
        portavozes = db.get_portavozes(banco['id'])
        portavozes_dict[banco['nome']] = [p['nome'] for p in portavozes]
    
    return IEDICalculatorBrandwatch(
        veiculos_relevantes=dominios_relevantes,
        veiculos_nicho=dominios_nicho,
        portavozes=portavozes_dict
    )
