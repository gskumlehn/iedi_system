"""
Teste de Conexão com Brandwatch API
"""
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
load_dotenv()

from app.services.brandwatch_service import BrandwatchService


def test_brandwatch_connection():
    """Testa conexão com Brandwatch API"""
    print("=" * 80)
    print("Teste de Conexão: Brandwatch API")
    print("=" * 80)
    
    service = BrandwatchService()
    
    print(f"\n1. Configuração:")
    print(f"   Username: {service.username}")
    print(f"   Project ID: {service.project_id}")
    print(f"   Password: {'*' * len(service.password) if service.password else 'NÃO CONFIGURADO'}")
    
    print(f"\n2. Testando conexão...")
    try:
        success = service.test_connection()
        if success:
            print("   ✓ Conexão estabelecida com sucesso!")
            
            # Tentar obter informações do projeto
            client = service._get_client()
            print(f"\n3. Informações do cliente:")
            print(f"   Tipo: {type(client)}")
            print(f"   Project ID: {client.project_id if hasattr(client, 'project_id') else 'N/A'}")
            
        else:
            print("   ✗ Falha na conexão")
            
    except Exception as e:
        print(f"   ✗ Erro: {e}")
        import traceback
        print("\n" + traceback.format_exc())


if __name__ == "__main__":
    test_brandwatch_connection()
