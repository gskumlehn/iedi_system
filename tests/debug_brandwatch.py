"""
Script de debug para testar conexão Brandwatch
"""
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

print("="*80)
print("DEBUG: Conexão Brandwatch")
print("="*80)
print()

# 1. Verificar variáveis de ambiente
print("1. Verificando variáveis de ambiente:")
print(f"   BRANDWATCH_USERNAME: {os.getenv('BRANDWATCH_USERNAME')}")
print(f"   BRANDWATCH_PASSWORD: {'***' if os.getenv('BRANDWATCH_PASSWORD') else 'None'}")
print(f"   BRANDWATCH_PROJECT_ID: {os.getenv('BRANDWATCH_PROJECT_ID')}")
print()

# 2. Verificar biblioteca bcr-api
print("2. Verificando biblioteca bcr-api:")
try:
    import bcr_api
    print(f"   ✓ bcr-api instalado (versão: {bcr_api.__version__ if hasattr(bcr_api, '__version__') else 'desconhecida'})")
except ImportError:
    print("   ✗ bcr-api NÃO instalado")
    print("   Execute: pip install bcr-api")
    exit(1)
print()

# 3. Tentar criar cliente
print("3. Tentando criar cliente Brandwatch:")
try:
    from bcr_api import Client
    
    username = os.getenv('BRANDWATCH_USERNAME')
    password = os.getenv('BRANDWATCH_PASSWORD')
    project_id = os.getenv('BRANDWATCH_PROJECT_ID')
    
    if not all([username, password, project_id]):
        print("   ✗ Variáveis de ambiente faltando")
        exit(1)
    
    print(f"   Conectando com username={username}, project={project_id}...")
    
    client = Client(
        username=username,
        password=password,
        project=int(project_id)
    )
    
    print("   ✓ Cliente criado com sucesso")
    print()
    
    # 4. Testar chamada à API
    print("4. Testando chamada à API:")
    try:
        # Tentar listar queries
        queries = client.get_queries()
        print(f"   ✓ API respondeu com sucesso")
        print(f"   Total de queries encontradas: {len(queries)}")
        
        if queries:
            print()
            print("   Queries disponíveis:")
            for q in queries[:5]:  # Mostrar apenas as 5 primeiras
                print(f"   - {q.get('name', 'Sem nome')}")
        
    except Exception as e:
        print(f"   ✗ Erro ao chamar API: {e}")
        print(f"   Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"   ✗ Erro ao criar cliente: {e}")
    print(f"   Tipo do erro: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
