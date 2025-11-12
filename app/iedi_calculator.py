"""
Calculadora IEDI - Índice de Exposição Digital na Imprensa
Adaptado para o sistema Flask/SQLite
"""
import json
from typing import Dict, List, Tuple
import re


class CalculadoraIEDI:
    """Classe para calcular o IEDI de menções da imprensa"""
    
    def __init__(self, db):
        self.db = db
        self.load_config()
    
    def load_config(self):
        """Carrega configurações do banco de dados"""
        configs = self.db.get_configuracoes()
        
        self.pesos = {
            'titulo': configs.get('peso_titulo', 100),
            'veiculo_relevante': configs.get('peso_veiculo_relevante', 95),
            'subtitulo_1p': configs.get('peso_subtitulo_1p', 80),
            'veiculo_nicho': configs.get('peso_veiculo_nicho', 54),
            'imagem': configs.get('peso_imagem', 20),
            'porta_voz': configs.get('peso_porta_voz', 20),
            'alcance_a': configs.get('peso_alcance_a', 91),
            'alcance_b': configs.get('peso_alcance_b', 85),
            'alcance_c': configs.get('peso_alcance_c', 24),
            'alcance_d': configs.get('peso_alcance_d', 20),
        }
        
        self.bonus_resposta = configs.get('bonus_resposta', 15) / 100.0
        
        self.alcance_grupos = {
            'A': {
                'min': configs.get('alcance_a_min', 29000001),
                'max': float('inf'),
                'peso': self.pesos['alcance_a']
            },
            'B': {
                'min': configs.get('alcance_b_min', 11000001),
                'max': configs.get('alcance_b_max', 29000000),
                'peso': self.pesos['alcance_b']
            },
            'C': {
                'min': configs.get('alcance_c_min', 500000),
                'max': configs.get('alcance_c_max', 11000000),
                'peso': self.pesos['alcance_c']
            },
            'D': {
                'min': 0,
                'max': configs.get('alcance_d_max', 500000),
                'peso': self.pesos['alcance_d']
            },
        }
        
        # Carregar dados do banco
        self.bancos_data = {}
        bancos = self.db.get_bancos(ativo_only=True)
        for banco in bancos:
            variacoes = json.loads(banco['variacoes'])
            self.bancos_data[banco['nome']] = variacoes
        
        self.veiculos_relevantes = {v['dominio']: v['nome'] for v in self.db.get_veiculos_relevantes() if v['ativo']}
        self.veiculos_nicho = {v['dominio'] for v in self.db.get_veiculos_nicho() if v['ativo']}
        
        self.porta_vozes_por_banco = {}
        porta_vozes = self.db.get_porta_vozes()
        for pv in porta_vozes:
            if pv['ativo']:
                banco_nome = pv['banco_nome']
                if banco_nome not in self.porta_vozes_por_banco:
                    self.porta_vozes_por_banco[banco_nome] = []
                self.porta_vozes_por_banco[banco_nome].append(pv['nome'])
        
        self.termos_resposta = [
            'segundo o banco', 'em nota', 'procurado, o banco informou',
            'o banco esclareceu', 'em comunicado', 'porta-voz afirmou',
            'assessoria de imprensa', 'o banco informou', 'em nota oficial',
            'comunicado à imprensa', 'por meio de nota', 'assessoria informou',
        ]
    
    def identificar_banco(self, texto: str) -> str:
        """Identifica qual banco é mencionado no texto"""
        if not texto:
            return None
        
        texto_lower = texto.lower()
        
        for banco, variacoes in self.bancos_data.items():
            for variacao in variacoes:
                if variacao.lower() in texto_lower:
                    return banco
        
        return None
    
    def verificar_titulo(self, row: Dict, banco: str) -> int:
        """Verifica se o banco é mencionado no título"""
        titulo = row.get('title', '') or row.get('snippet', '')
        
        if not titulo:
            return 0
        
        titulo_lower = titulo.lower()
        variacoes = self.bancos_data.get(banco, [])
        
        for variacao in variacoes:
            if variacao.lower() in titulo_lower:
                return 1
        
        return 0
    
    def verificar_subtitulo_1p(self, row: Dict, banco: str) -> int:
        """Verifica se o banco é mencionado no subtítulo ou 1º parágrafo"""
        snippet = row.get('snippet', '')
        
        if not snippet:
            return 0
        
        texto = snippet[:280].lower()
        variacoes = self.bancos_data.get(banco, [])
        
        for variacao in variacoes:
            if variacao.lower() in texto:
                return 1
        
        return 0
    
    def verificar_veiculo_relevante(self, row: Dict) -> int:
        """Verifica se a menção vem de um veículo relevante"""
        domain = row.get('domain', '')
        
        if not domain:
            return 0
        
        if domain in self.veiculos_relevantes:
            return 1
        
        for veiculo_domain in self.veiculos_relevantes.keys():
            if veiculo_domain in domain or domain in veiculo_domain:
                return 1
        
        return 0
    
    def verificar_veiculo_nicho(self, row: Dict) -> int:
        """Verifica se a menção vem de um veículo de nicho"""
        domain = row.get('domain', '')
        
        if not domain:
            return 0
        
        if domain in self.veiculos_nicho:
            return 1
        
        for nicho_domain in self.veiculos_nicho:
            if nicho_domain in domain or domain in nicho_domain:
                return 1
        
        return 0
    
    def verificar_imagem(self, row: Dict) -> int:
        """Verifica se há imagem associada à menção"""
        image_info = row.get('imageInfo', [])
        media_urls = row.get('mediaUrls', [])
        
        if image_info and len(image_info) > 0:
            return 1
        
        if media_urls and len(media_urls) > 0:
            return 1
        
        return 0
    
    def verificar_porta_voz(self, row: Dict, banco: str) -> int:
        """Verifica se há menção a porta-voz do banco"""
        snippet = row.get('snippet', '')
        
        if not snippet:
            return 0
        
        porta_vozes = self.porta_vozes_por_banco.get(banco, [])
        
        for porta_voz in porta_vozes:
            if porta_voz.lower() in snippet.lower():
                return 1
        
        return 0
    
    def classificar_alcance(self, row: Dict) -> Tuple[str, int]:
        """Classifica o veículo em grupo de alcance"""
        monthly_visitors = row.get('monthlyVisitors', 0) or 0
        
        for grupo, config in self.alcance_grupos.items():
            if config['min'] <= monthly_visitors <= config['max']:
                return grupo, config['peso']
        
        return 'D', self.alcance_grupos['D']['peso']
    
    def verificar_resposta_banco(self, row: Dict) -> int:
        """Verifica se há resposta ou posicionamento oficial do banco"""
        snippet = row.get('snippet', '')
        
        if not snippet:
            return 0
        
        snippet_lower = snippet.lower()
        
        for termo in self.termos_resposta:
            if termo in snippet_lower:
                return 1
        
        return 0
    
    def calcular_nota_noticia(self, row: Dict, banco: str) -> Dict:
        """Calcula a nota IEDI de uma notícia individual"""
        variaveis = {
            'titulo': self.verificar_titulo(row, banco),
            'veiculo_relevante': self.verificar_veiculo_relevante(row),
            'subtitulo_1p': self.verificar_subtitulo_1p(row, banco),
            'veiculo_nicho': self.verificar_veiculo_nicho(row),
            'imagem': self.verificar_imagem(row),
            'porta_voz': self.verificar_porta_voz(row, banco),
        }
        
        grupo_alcance, peso_alcance = self.classificar_alcance(row)
        variaveis[f'alcance_{grupo_alcance.lower()}'] = 1
        
        soma_pesos = 0
        soma_ponderada = 0
        
        for var, valor in variaveis.items():
            if valor == 1:
                peso = self.pesos.get(var, 0)
                if peso > 0:
                    soma_pesos += peso
                    soma_ponderada += peso
        
        sentiment = row.get('sentiment', 'neutral')
        
        if soma_pesos == 0:
            nota_base = 0
        else:
            nota_base = soma_ponderada / soma_pesos
        
        if sentiment == 'negative':
            nota_base = -nota_base
            
            tem_resposta = self.verificar_resposta_banco(row)
            if tem_resposta:
                nota_base = nota_base * (1 + self.bonus_resposta)
                variaveis['resposta_banco'] = 1
            else:
                variaveis['resposta_banco'] = 0
        elif sentiment == 'neutral':
            nota_base = 0
            variaveis['resposta_banco'] = 0
        else:
            variaveis['resposta_banco'] = 0
        
        nota_final = (nota_base + 1) * 5
        
        return {
            'nota': nota_final,
            'nota_base': nota_base,
            'sentiment': sentiment,
            'grupo_alcance': grupo_alcance,
            'variaveis': variaveis,
            'soma_pesos': soma_pesos,
        }
    
    def calcular_iedi_banco(self, mencoes: List[Dict], banco: str, banco_id: int) -> Dict:
        """Calcula o IEDI de um banco"""
        if len(mencoes) == 0:
            return {
                'banco': banco,
                'banco_id': banco_id,
                'iedi_medio': 0,
                'volume_total': 0,
                'volume_positivo': 0,
                'volume_negativo': 0,
                'volume_neutro': 0,
                'positividade': 0,
                'negatividade': 0,
                'resultados': []
            }
        
        resultados = []
        for mencao in mencoes:
            resultado = self.calcular_nota_noticia(mencao, banco)
            resultado['mention_id'] = mencao.get('id')
            resultado['date'] = mencao.get('date', '')
            resultado['url'] = mencao.get('url', '')
            resultado['title'] = mencao.get('title', '')
            resultado['domain'] = mencao.get('domain', '')
            resultados.append(resultado)
        
        volume_total = len(resultados)
        volume_positivo = sum(1 for r in resultados if r['sentiment'] == 'positive')
        volume_negativo = sum(1 for r in resultados if r['sentiment'] == 'negative')
        volume_neutro = sum(1 for r in resultados if r['sentiment'] == 'neutral')
        
        positividade = (volume_positivo / volume_total * 100) if volume_total > 0 else 0
        negatividade = (volume_negativo / volume_total * 100) if volume_total > 0 else 0
        
        iedi_medio = sum(r['nota'] for r in resultados) / volume_total if volume_total > 0 else 0
        
        return {
            'banco': banco,
            'banco_id': banco_id,
            'iedi_medio': iedi_medio,
            'volume_total': volume_total,
            'volume_positivo': volume_positivo,
            'volume_negativo': volume_negativo,
            'volume_neutro': volume_neutro,
            'positividade': positividade,
            'negatividade': negatividade,
            'resultados': resultados
        }
    
    def calcular_iedi_final_com_balizamento(self, resultados_bancos: List[Dict]) -> List[Dict]:
        """Calcula o IEDI final com balizamento por volume"""
        total_positivas = sum(r['volume_positivo'] for r in resultados_bancos)
        
        resultados_finais = []
        
        for resultado in resultados_bancos:
            banco = resultado['banco']
            banco_id = resultado['banco_id']
            iedi_medio = resultado['iedi_medio']
            volume_positivo = resultado['volume_positivo']
            
            if total_positivas > 0:
                proporcao_positivas = volume_positivo / total_positivas
            else:
                proporcao_positivas = 0
            
            iedi_final = iedi_medio * (1 + proporcao_positivas)
            
            resultados_finais.append({
                'banco': banco,
                'banco_id': banco_id,
                'iedi_final': iedi_final,
                'iedi_medio': iedi_medio,
                'volume_total': resultado['volume_total'],
                'volume_positivo': volume_positivo,
                'volume_negativo': resultado['volume_negativo'],
                'volume_neutro': resultado['volume_neutro'],
                'positividade': resultado['positividade'],
                'negatividade': resultado['negatividade'],
                'proporcao_positivas': proporcao_positivas * 100,
            })
        
        resultados_finais.sort(key=lambda x: x['iedi_final'], reverse=True)
        
        return resultados_finais
