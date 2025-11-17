#!/usr/bin/env python3
"""
Script para executar migrations SQL no Google BigQuery.

Uso:
    python sql/run_migrations.py

Variáveis de ambiente necessárias:
    GOOGLE_CLOUD_PROJECT_ID - ID do projeto GCP
    GOOGLE_APPLICATION_CREDENTIALS - Caminho para arquivo JSON do service account
"""

import os
import sys
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

def get_bigquery_client():
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT_ID não definido")
    
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS não definido")
    
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_path}")
    
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    
    client = bigquery.Client(
        project=project_id,
        credentials=credentials
    )
    
    return client


def get_sql_files(sql_dir: Path):
    sql_files = sorted(sql_dir.glob('*.sql'))
    
    create_dataset = [f for f in sql_files if 'create_dataset' in f.name]
    create_tables = [f for f in sql_files if 'create_table' in f.name]
    inserts = [f for f in sql_files if 'insert' in f.name]
    
    return create_dataset + create_tables + inserts


def execute_sql_file(client: bigquery.Client, sql_file: Path):
    print(f"\n{'='*80}")
    print(f"Executando: {sql_file.name}")
    print('='*80)
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    if not sql_content.strip():
        print("⚠️  Arquivo vazio, pulando...")
        return True
    
    try:
        query_job = client.query(sql_content)
        query_job.result()
        
        print(f"✓ {sql_file.name} executado com sucesso")
        
        if query_job.total_bytes_processed:
            bytes_processed = query_job.total_bytes_processed / (1024 * 1024)
            print(f"  Bytes processados: {bytes_processed:.2f} MB")
        
        if query_job.num_dml_affected_rows is not None:
            print(f"  Linhas afetadas: {query_job.num_dml_affected_rows}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao executar {sql_file.name}:")
        print(f"  {str(e)}")
        return False


def main():
    print("="*80)
    print("MIGRATIONS BIGQUERY - Sistema IEDI")
    print("="*80)
    print()
    
    try:
        print("Conectando ao BigQuery...")
        client = get_bigquery_client()
        print(f"✓ Conectado ao projeto: {client.project}")
        print()
        
        print("Removendo schema 'iedi' existente (se houver)...")
        try:
            client.query("DROP SCHEMA IF EXISTS iedi CASCADE").result()
            print("✓ Schema 'iedi' removido")
        except Exception as e:
            print(f"⚠️  Aviso ao remover schema: {str(e)}")
        print()
        
        sql_dir = Path(__file__).parent
        sql_files = get_sql_files(sql_dir)
        
        if not sql_files:
            print("✗ Nenhum arquivo SQL encontrado")
            return 1
        
        print(f"Encontrados {len(sql_files)} arquivos SQL:")
        for sql_file in sql_files:
            print(f"  - {sql_file.name}")
        print()
        
        input("Pressione ENTER para continuar ou Ctrl+C para cancelar...")
        print()
        
        success_count = 0
        error_count = 0
        
        for sql_file in sql_files:
            if execute_sql_file(client, sql_file):
                success_count += 1
            else:
                error_count += 1
        
        print()
        print("="*80)
        print("RESUMO")
        print("="*80)
        print(f"Total de arquivos: {len(sql_files)}")
        print(f"Executados com sucesso: {success_count}")
        print(f"Erros: {error_count}")
        print()
        
        if error_count == 0:
            print("✓ Todas as migrations foram executadas com sucesso!")
            return 0
        else:
            print("✗ Algumas migrations falharam. Verifique os erros acima.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n✗ Operação cancelada pelo usuário")
        return 1
        
    except Exception as e:
        print(f"\n✗ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
