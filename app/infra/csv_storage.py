import pandas as pd
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class CSVStorage:
    """
    Classe para persistência de dados em CSV usando Pandas.
    Criada para melhorar performance em relação ao BigQuery.
    """
    
    DATA_DIR = Path(__file__).parent.parent.parent / "data"
    
    @classmethod
    def ensure_data_dir(cls):
        """Garante que o diretório data/ existe"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def save_mentions(cls, mentions: List[Dict[str, Any]], analysis_id: str):
        """
        Salva mentions em CSV.
        
        Args:
            mentions: Lista de dicionários com dados das mentions
            analysis_id: ID da análise (para nomear o arquivo)
        """
        cls.ensure_data_dir()
        
        if not mentions:
            print(f"[CSVStorage] Nenhuma mention para salvar (analysis_id={analysis_id})")
            return
        
        # Converter para DataFrame
        df = pd.DataFrame(mentions)
        
        # Garantir que colunas existam (mesmo que vazias)
        expected_columns = [
            'id', 'url', 'title', 'snippet', 'full_text', 'domain',
            'published_date', 'sentiment', 'categories', 'monthly_visitors',
            'created_at', 'updated_at'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = None
        
        # Reordenar colunas
        df = df[expected_columns]
        
        # Caminho do arquivo
        file_path = cls.DATA_DIR / f"mentions_{analysis_id}.csv"
        
        # Salvar CSV (append se já existir)
        if file_path.exists():
            # Ler CSV existente
            existing_df = pd.read_csv(file_path)
            
            # Concatenar com novos dados
            df = pd.concat([existing_df, df], ignore_index=True)
            
            # Remover duplicatas por 'id'
            df = df.drop_duplicates(subset=['id'], keep='last')
        
        # Salvar CSV
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        print(f"[CSVStorage] Salvos {len(mentions)} mentions em {file_path}")
    
    @classmethod
    def save_mention_analyses(cls, mention_analyses: List[Dict[str, Any]], analysis_id: str):
        """
        Salva mention_analysis em CSV.
        
        Args:
            mention_analyses: Lista de dicionários com dados das mention_analysis
            analysis_id: ID da análise (para nomear o arquivo)
        """
        cls.ensure_data_dir()
        
        if not mention_analyses:
            print(f"[CSVStorage] Nenhuma mention_analysis para salvar (analysis_id={analysis_id})")
            return
        
        # Converter para DataFrame
        df = pd.DataFrame(mention_analyses)
        
        # Garantir que colunas existam (mesmo que vazias)
        expected_columns = [
            'mention_id', 'bank_name', 'sentiment', 'reach_group',
            'niche_vehicle', 'title_mentioned', 'subtitle_used', 'subtitle_mentioned',
            'iedi_score', 'created_at', 'updated_at'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = None
        
        # Reordenar colunas
        df = df[expected_columns]
        
        # Caminho do arquivo
        file_path = cls.DATA_DIR / f"mention_analysis_{analysis_id}.csv"
        
        # Salvar CSV (append se já existir)
        if file_path.exists():
            # Ler CSV existente
            existing_df = pd.read_csv(file_path)
            
            # Concatenar com novos dados
            df = pd.concat([existing_df, df], ignore_index=True)
            
            # Remover duplicatas por 'mention_id' e 'bank_name'
            df = df.drop_duplicates(subset=['mention_id', 'bank_name'], keep='last')
        
        # Salvar CSV
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        print(f"[CSVStorage] Salvos {len(mention_analyses)} mention_analysis em {file_path}")
    
    @classmethod
    def load_mentions(cls, analysis_id: str) -> pd.DataFrame:
        """
        Carrega mentions de um CSV.
        
        Args:
            analysis_id: ID da análise
        
        Returns:
            DataFrame com mentions
        """
        file_path = cls.DATA_DIR / f"mentions_{analysis_id}.csv"
        
        if not file_path.exists():
            print(f"[CSVStorage] Arquivo não encontrado: {file_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        print(f"[CSVStorage] Carregados {len(df)} mentions de {file_path}")
        return df
    
    @classmethod
    def load_mention_analyses(cls, analysis_id: str) -> pd.DataFrame:
        """
        Carrega mention_analysis de um CSV.
        
        Args:
            analysis_id: ID da análise
        
        Returns:
            DataFrame com mention_analysis
        """
        file_path = cls.DATA_DIR / f"mention_analysis_{analysis_id}.csv"
        
        if not file_path.exists():
            print(f"[CSVStorage] Arquivo não encontrado: {file_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        print(f"[CSVStorage] Carregados {len(df)} mention_analysis de {file_path}")
        return df
