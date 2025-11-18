"""
Teste simples para verificar import de bcr_api
"""
print("="*80)
print("Teste de Import: bcr_api")
print("="*80)
print()

print("1. Tentando importar bcr_api...")
try:
    import bcr_api
    print(f"   ✓ bcr_api importado com sucesso")
    print(f"   Versão: {bcr_api.__version__ if hasattr(bcr_api, '__version__') else 'desconhecida'}")
    print(f"   Localização: {bcr_api.__file__}")
except ImportError as e:
    print(f"   ✗ Erro ao importar bcr_api: {e}")
    exit(1)
print()

print("2. Tentando importar Client de bcr_api...")
try:
    from bcr_api import Client
    print(f"   ✓ Client importado com sucesso")
    print(f"   Classe: {Client}")
except ImportError as e:
    print(f"   ✗ Erro ao importar Client: {e}")
    exit(1)
except Exception as e:
    print(f"   ✗ Outro erro: {type(e).__name__}: {e}")
    exit(1)
print()

print("3. Verificando atributos de Client...")
try:
    import inspect
    methods = [m for m in dir(Client) if not m.startswith('_')]
    print(f"   Métodos públicos: {', '.join(methods[:5])}...")
except Exception as e:
    print(f"   ✗ Erro: {e}")
print()

print("="*80)
print("✓ Todos os imports funcionaram!")
print("="*80)
