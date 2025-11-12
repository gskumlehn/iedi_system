"""
Modelos do banco de dados SQLite para o sistema IEDI
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json


class Database:
    def __init__(self, db_path: str = "data/iedi.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializa o banco de dados com todas as tabelas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de bancos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bancos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                variacoes TEXT NOT NULL,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de porta-vozes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS porta_vozes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                banco_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                cargo TEXT,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (banco_id) REFERENCES bancos(id)
            )
        ''')
        
        # Tabela de veículos relevantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS veiculos_relevantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                dominio TEXT NOT NULL UNIQUE,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de veículos de nicho
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS veiculos_nicho (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                dominio TEXT NOT NULL UNIQUE,
                categoria TEXT,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de configurações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT NOT NULL UNIQUE,
                valor TEXT NOT NULL,
                descricao TEXT,
                tipo TEXT DEFAULT 'string',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de configuração Brandwatch
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brandwatch_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                project TEXT NOT NULL,
                query_name TEXT NOT NULL,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de análises
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_inicio TIMESTAMP NOT NULL,
                data_fim TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'processando',
                total_mencoes INTEGER DEFAULT 0,
                mensagem_erro TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de resultados IEDI
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resultados_iedi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analise_id INTEGER NOT NULL,
                banco_id INTEGER NOT NULL,
                iedi_medio INTEGER NOT NULL,
                iedi_final INTEGER NOT NULL,
                volume_total INTEGER DEFAULT 0,
                volume_positivo INTEGER DEFAULT 0,
                volume_negativo INTEGER DEFAULT 0,
                volume_neutro INTEGER DEFAULT 0,
                positividade INTEGER DEFAULT 0,
                negatividade INTEGER DEFAULT 0,
                proporcao_positivas INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analise_id) REFERENCES analises(id),
                FOREIGN KEY (banco_id) REFERENCES bancos(id)
            )
        ''')
        
        # Tabela de menções
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mencoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analise_id INTEGER NOT NULL,
                banco_id INTEGER NOT NULL,
                mention_id TEXT,
                titulo TEXT,
                snippet TEXT,
                url TEXT,
                domain TEXT,
                sentiment TEXT,
                monthly_visitors INTEGER DEFAULT 0,
                data_mencao TIMESTAMP,
                nota INTEGER DEFAULT 0,
                grupo_alcance TEXT,
                variaveis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analise_id) REFERENCES analises(id),
                FOREIGN KEY (banco_id) REFERENCES bancos(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Inserir configurações padrão
        self.init_default_config()
    
    def init_default_config(self):
        """Insere configurações padrão se não existirem"""
        configs = [
            ('peso_titulo', '100', 'Peso da variável Título', 'number'),
            ('peso_veiculo_relevante', '95', 'Peso da variável Veículo Relevante', 'number'),
            ('peso_subtitulo_1p', '80', 'Peso da variável Subtítulo/1º Parágrafo', 'number'),
            ('peso_veiculo_nicho', '54', 'Peso da variável Veículo de Nicho', 'number'),
            ('peso_imagem', '20', 'Peso da variável Imagem', 'number'),
            ('peso_porta_voz', '20', 'Peso da variável Porta-voz', 'number'),
            ('peso_alcance_a', '91', 'Peso do Alcance Grupo A', 'number'),
            ('peso_alcance_b', '85', 'Peso do Alcance Grupo B', 'number'),
            ('peso_alcance_c', '24', 'Peso do Alcance Grupo C', 'number'),
            ('peso_alcance_d', '20', 'Peso do Alcance Grupo D', 'number'),
            ('bonus_resposta', '15', 'Bônus de resposta do banco (%)', 'number'),
            ('alcance_a_min', '29000001', 'Visitantes mínimos Grupo A', 'number'),
            ('alcance_b_min', '11000001', 'Visitantes mínimos Grupo B', 'number'),
            ('alcance_b_max', '29000000', 'Visitantes máximos Grupo B', 'number'),
            ('alcance_c_min', '500000', 'Visitantes mínimos Grupo C', 'number'),
            ('alcance_c_max', '11000000', 'Visitantes máximos Grupo C', 'number'),
            ('alcance_d_max', '500000', 'Visitantes máximos Grupo D', 'number'),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for chave, valor, descricao, tipo in configs:
            cursor.execute('''
                INSERT OR IGNORE INTO configuracoes (chave, valor, descricao, tipo)
                VALUES (?, ?, ?, ?)
            ''', (chave, valor, descricao, tipo))
        
        conn.commit()
        conn.close()
    
    # CRUD Bancos
    def get_bancos(self, ativo_only=False) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if ativo_only:
            cursor.execute('SELECT * FROM bancos WHERE ativo = 1 ORDER BY nome')
        else:
            cursor.execute('SELECT * FROM bancos ORDER BY nome')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_banco(self, banco_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bancos WHERE id = ?', (banco_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def create_banco(self, nome: str, variacoes: List[str], ativo: bool = True) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bancos (nome, variacoes, ativo)
            VALUES (?, ?, ?)
        ''', (nome, json.dumps(variacoes), 1 if ativo else 0))
        banco_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return banco_id
    
    def update_banco(self, banco_id: int, nome: str, variacoes: List[str], ativo: bool):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE bancos
            SET nome = ?, variacoes = ?, ativo = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (nome, json.dumps(variacoes), 1 if ativo else 0, banco_id))
        conn.commit()
        conn.close()
    
    def delete_banco(self, banco_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM bancos WHERE id = ?', (banco_id,))
        conn.commit()
        conn.close()
    
    # CRUD Porta-vozes
    def get_porta_vozes(self, banco_id: Optional[int] = None) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if banco_id:
            cursor.execute('''
                SELECT pv.*, b.nome as banco_nome
                FROM porta_vozes pv
                JOIN bancos b ON pv.banco_id = b.id
                WHERE pv.banco_id = ?
                ORDER BY pv.nome
            ''', (banco_id,))
        else:
            cursor.execute('''
                SELECT pv.*, b.nome as banco_nome
                FROM porta_vozes pv
                JOIN bancos b ON pv.banco_id = b.id
                ORDER BY b.nome, pv.nome
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def create_porta_voz(self, banco_id: int, nome: str, cargo: str = None, ativo: bool = True) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO porta_vozes (banco_id, nome, cargo, ativo)
            VALUES (?, ?, ?, ?)
        ''', (banco_id, nome, cargo, 1 if ativo else 0))
        pv_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pv_id
    
    def update_porta_voz(self, pv_id: int, banco_id: int, nome: str, cargo: str = None, ativo: bool = True):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE porta_vozes
            SET banco_id = ?, nome = ?, cargo = ?, ativo = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (banco_id, nome, cargo, 1 if ativo else 0, pv_id))
        conn.commit()
        conn.close()
    
    def delete_porta_voz(self, pv_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM porta_vozes WHERE id = ?', (pv_id,))
        conn.commit()
        conn.close()
    
    # CRUD Veículos Relevantes
    def get_veiculos_relevantes(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM veiculos_relevantes ORDER BY nome')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def create_veiculo_relevante(self, nome: str, dominio: str, ativo: bool = True) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO veiculos_relevantes (nome, dominio, ativo)
            VALUES (?, ?, ?)
        ''', (nome, dominio, 1 if ativo else 0))
        vr_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return vr_id
    
    def update_veiculo_relevante(self, vr_id: int, nome: str, dominio: str, ativo: bool):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE veiculos_relevantes
            SET nome = ?, dominio = ?, ativo = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (nome, dominio, 1 if ativo else 0, vr_id))
        conn.commit()
        conn.close()
    
    def delete_veiculo_relevante(self, vr_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM veiculos_relevantes WHERE id = ?', (vr_id,))
        conn.commit()
        conn.close()
    
    # CRUD Veículos de Nicho
    def get_veiculos_nicho(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM veiculos_nicho ORDER BY nome')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def create_veiculo_nicho(self, nome: str, dominio: str, categoria: str = None, ativo: bool = True) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO veiculos_nicho (nome, dominio, categoria, ativo)
            VALUES (?, ?, ?, ?)
        ''', (nome, dominio, categoria, 1 if ativo else 0))
        vn_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return vn_id
    
    def update_veiculo_nicho(self, vn_id: int, nome: str, dominio: str, categoria: str = None, ativo: bool = True):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE veiculos_nicho
            SET nome = ?, dominio = ?, categoria = ?, ativo = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (nome, dominio, categoria, 1 if ativo else 0, vn_id))
        conn.commit()
        conn.close()
    
    def delete_veiculo_nicho(self, vn_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM veiculos_nicho WHERE id = ?', (vn_id,))
        conn.commit()
        conn.close()
    
    # Configurações
    def get_configuracoes(self) -> Dict[str, any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT chave, valor, tipo FROM configuracoes')
        rows = cursor.fetchall()
        conn.close()
        
        configs = {}
        for row in rows:
            chave = row['chave']
            valor = row['valor']
            tipo = row['tipo']
            
            if tipo == 'number':
                configs[chave] = float(valor)
            elif tipo == 'json':
                configs[chave] = json.loads(valor)
            elif tipo == 'boolean':
                configs[chave] = valor.lower() in ('true', '1', 'yes')
            else:
                configs[chave] = valor
        
        return configs
    
    def update_configuracao(self, chave: str, valor: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE configuracoes
            SET valor = ?, updated_at = CURRENT_TIMESTAMP
            WHERE chave = ?
        ''', (valor, chave))
        conn.commit()
        conn.close()
    
    # Brandwatch Config
    def get_brandwatch_config(self) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM brandwatch_config WHERE ativo = 1 LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def save_brandwatch_config(self, email: str, password: str, project: str, query_name: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Desativar configs antigas
        cursor.execute('UPDATE brandwatch_config SET ativo = 0')
        
        # Inserir nova config
        cursor.execute('''
            INSERT INTO brandwatch_config (email, password, project, query_name, ativo)
            VALUES (?, ?, ?, ?, 1)
        ''', (email, password, project, query_name))
        
        conn.commit()
        conn.close()
    
    # Análises
    def create_analise(self, data_inicio: str, data_fim: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analises (data_inicio, data_fim, status)
            VALUES (?, ?, 'processando')
        ''', (data_inicio, data_fim))
        analise_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analise_id
    
    def update_analise_status(self, analise_id: int, status: str, total_mencoes: int = None, mensagem_erro: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if total_mencoes is not None:
            cursor.execute('''
                UPDATE analises
                SET status = ?, total_mencoes = ?, mensagem_erro = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, total_mencoes, mensagem_erro, analise_id))
        else:
            cursor.execute('''
                UPDATE analises
                SET status = ?, mensagem_erro = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, mensagem_erro, analise_id))
        
        conn.commit()
        conn.close()
    
    def get_analises(self, limit: int = 50) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM analises
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_analise(self, analise_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM analises WHERE id = ?', (analise_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # Resultados IEDI
    def save_resultado_iedi(self, analise_id: int, banco_id: int, resultado: Dict):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO resultados_iedi (
                analise_id, banco_id, iedi_medio, iedi_final,
                volume_total, volume_positivo, volume_negativo, volume_neutro,
                positividade, negatividade, proporcao_positivas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analise_id, banco_id,
            int(resultado['iedi_medio'] * 100),
            int(resultado['iedi_final'] * 100),
            resultado['volume_total'],
            resultado['volume_positivo'],
            resultado['volume_negativo'],
            resultado['volume_neutro'],
            int(resultado['positividade'] * 100),
            int(resultado['negatividade'] * 100),
            int(resultado['proporcao_positivas'] * 100)
        ))
        conn.commit()
        conn.close()
    
    def get_resultados_iedi(self, analise_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, b.nome as banco_nome
            FROM resultados_iedi r
            JOIN bancos b ON r.banco_id = b.id
            WHERE r.analise_id = ?
            ORDER BY r.iedi_final DESC
        ''', (analise_id,))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            # Converter de volta para float
            result['iedi_medio'] = result['iedi_medio'] / 100.0
            result['iedi_final'] = result['iedi_final'] / 100.0
            result['positividade'] = result['positividade'] / 100.0
            result['negatividade'] = result['negatividade'] / 100.0
            result['proporcao_positivas'] = result['proporcao_positivas'] / 100.0
            results.append(result)
        
        return results
    
    # Menções
    def save_mencao(self, mencao: Dict):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mencoes (
                analise_id, banco_id, mention_id, titulo, snippet, url, domain,
                sentiment, monthly_visitors, data_mencao, nota, grupo_alcance, variaveis
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            mencao['analise_id'], mencao['banco_id'], mencao.get('mention_id'),
            mencao.get('titulo'), mencao.get('snippet'), mencao.get('url'), mencao.get('domain'),
            mencao.get('sentiment'), mencao.get('monthly_visitors', 0),
            mencao.get('data_mencao'), int(mencao.get('nota', 0) * 100),
            mencao.get('grupo_alcance'), json.dumps(mencao.get('variaveis', {}))
        ))
        conn.commit()
        conn.close()
    
    def get_mencoes(self, analise_id: int, banco_id: Optional[int] = None, limit: int = 1000) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if banco_id:
            cursor.execute('''
                SELECT * FROM mencoes
                WHERE analise_id = ? AND banco_id = ?
                ORDER BY nota DESC
                LIMIT ?
            ''', (analise_id, banco_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM mencoes
                WHERE analise_id = ?
                ORDER BY nota DESC
                LIMIT ?
            ''', (analise_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        mencoes = []
        for row in rows:
            mencao = dict(row)
            mencao['nota'] = mencao['nota'] / 100.0
            mencao['variaveis'] = json.loads(mencao['variaveis']) if mencao['variaveis'] else {}
            mencoes.append(mencao)
        
        return mencoes
