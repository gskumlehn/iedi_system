"""
Script de migração do banco de dados IEDI
Adiciona colunas faltantes para compatibilidade com v2.0+
"""
import sqlite3
import os

DB_PATH = "data/iedi.db"

def migrate():
    """Executa migrações necessárias"""
    
    if not os.path.exists(DB_PATH):
        print("❌ Banco de dados não encontrado. Execute o sistema primeiro para criar o banco.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔄 Iniciando migração do banco de dados...")
    
    # Verificar e adicionar colunas na tabela analises
    try:
        cursor.execute("PRAGMA table_info(analises)")
        columns = [col[1] for col in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'periodo_referencia' not in columns:
            migrations_needed.append(('periodo_referencia', 'TEXT'))
        
        if 'tipo' not in columns:
            migrations_needed.append(('tipo', "TEXT DEFAULT 'mensal'"))
        
        if migrations_needed:
            print(f"📝 Adicionando {len(migrations_needed)} colunas à tabela 'analises'...")
            
            for col_name, col_type in migrations_needed:
                try:
                    cursor.execute(f"ALTER TABLE analises ADD COLUMN {col_name} {col_type}")
                    print(f"  ✅ Coluna '{col_name}' adicionada")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"  ⚠️  Coluna '{col_name}' já existe")
                    else:
                        raise
        else:
            print("✅ Tabela 'analises' já está atualizada")
    
    except Exception as e:
        print(f"❌ Erro ao migrar tabela 'analises': {e}")
        conn.close()
        return
    
    # Verificar e criar tabela periodos_banco se não existir
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS periodos_banco (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analise_id INTEGER NOT NULL,
                banco_id INTEGER NOT NULL,
                data_divulgacao DATE NOT NULL,
                data_inicio DATE NOT NULL,
                data_fim DATE NOT NULL,
                dias_coleta INTEGER DEFAULT 2,
                total_mencoes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analise_id) REFERENCES analises(id),
                FOREIGN KEY (banco_id) REFERENCES bancos(id)
            )
        """)
        print("✅ Tabela 'periodos_banco' verificada/criada")
    except Exception as e:
        print(f"❌ Erro ao criar tabela 'periodos_banco': {e}")
    
    # Verificar e adicionar coluna category_detail na tabela mencoes
    try:
        cursor.execute("PRAGMA table_info(mencoes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'category_detail' not in columns:
            cursor.execute("ALTER TABLE mencoes ADD COLUMN category_detail TEXT")
            print("✅ Coluna 'category_detail' adicionada à tabela 'mencoes'")
        else:
            print("✅ Tabela 'mencoes' já está atualizada")
    
    except Exception as e:
        print(f"❌ Erro ao migrar tabela 'mencoes': {e}")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Migração concluída com sucesso!")
    print("💡 Reinicie o sistema Docker para aplicar as mudanças:")
    print("   docker-compose down && docker-compose up -d")

if __name__ == "__main__":
    migrate()
