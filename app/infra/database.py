import os
import mysql.connector
from contextlib import contextmanager
from typing import Generator

def get_db_config():
    """Retorna configuração do banco de dados a partir de variáveis de ambiente"""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'iedi'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }

@contextmanager
def get_connection() -> Generator:
    """Context manager para conexão com o banco de dados"""
    conn = None
    try:
        conn = mysql.connector.connect(**get_db_config())
        yield conn
    finally:
        if conn and conn.is_connected():
            conn.close()

@contextmanager
def get_cursor(dictionary=True) -> Generator:
    """Context manager para cursor do banco de dados"""
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
