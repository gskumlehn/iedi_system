"""
Sistema IEDI - Aplicação Flask Principal
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from app.models import Database
from app.iedi_calculator import CalculadoraIEDI
import json
import os
from datetime import datetime

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Inicializar banco de dados
db = Database()

# Rotas de páginas HTML
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bancos')
def bancos_page():
    return render_template('bancos.html')

@app.route('/porta-vozes')
def porta_vozes_page():
    return render_template('porta_vozes.html')

@app.route('/veiculos')
def veiculos_page():
    return render_template('veiculos.html')

@app.route('/configuracoes')
def configuracoes_page():
    return render_template('configuracoes.html')

@app.route('/analises')
def analises_page():
    return render_template('analises.html')

@app.route('/analise/<int:analise_id>')
def analise_detalhes_page(analise_id):
    return render_template('analise_detalhes.html', analise_id=analise_id)

# API - Bancos
@app.route('/api/bancos', methods=['GET'])
def get_bancos():
    bancos = db.get_bancos()
    # Converter variacoes de JSON string para array
    for banco in bancos:
        banco['variacoes'] = json.loads(banco['variacoes'])
    return jsonify(bancos)

@app.route('/api/bancos', methods=['POST'])
def create_banco():
    data = request.json
    banco_id = db.create_banco(
        nome=data['nome'],
        variacoes=data['variacoes'],
        ativo=data.get('ativo', True)
    )
    return jsonify({'id': banco_id, 'success': True})

@app.route('/api/bancos/<int:banco_id>', methods=['PUT'])
def update_banco(banco_id):
    data = request.json
    db.update_banco(
        banco_id=banco_id,
        nome=data['nome'],
        variacoes=data['variacoes'],
        ativo=data.get('ativo', True)
    )
    return jsonify({'success': True})

@app.route('/api/bancos/<int:banco_id>', methods=['DELETE'])
def delete_banco(banco_id):
    db.delete_banco(banco_id)
    return jsonify({'success': True})

# API - Porta-vozes
@app.route('/api/porta-vozes', methods=['GET'])
def get_porta_vozes():
    banco_id = request.args.get('banco_id', type=int)
    porta_vozes = db.get_porta_vozes(banco_id)
    return jsonify(porta_vozes)

@app.route('/api/porta-vozes', methods=['POST'])
def create_porta_voz():
    data = request.json
    pv_id = db.create_porta_voz(
        banco_id=data['banco_id'],
        nome=data['nome'],
        cargo=data.get('cargo'),
        ativo=data.get('ativo', True)
    )
    return jsonify({'id': pv_id, 'success': True})

@app.route('/api/porta-vozes/<int:pv_id>', methods=['PUT'])
def update_porta_voz(pv_id):
    data = request.json
    db.update_porta_voz(
        pv_id=pv_id,
        banco_id=data['banco_id'],
        nome=data['nome'],
        cargo=data.get('cargo'),
        ativo=data.get('ativo', True)
    )
    return jsonify({'success': True})

@app.route('/api/porta-vozes/<int:pv_id>', methods=['DELETE'])
def delete_porta_voz(pv_id):
    db.delete_porta_voz(pv_id)
    return jsonify({'success': True})

# API - Veículos Relevantes
@app.route('/api/veiculos-relevantes', methods=['GET'])
def get_veiculos_relevantes():
    veiculos = db.get_veiculos_relevantes()
    return jsonify(veiculos)

@app.route('/api/veiculos-relevantes', methods=['POST'])
def create_veiculo_relevante():
    data = request.json
    vr_id = db.create_veiculo_relevante(
        nome=data['nome'],
        dominio=data['dominio'],
        ativo=data.get('ativo', True)
    )
    return jsonify({'id': vr_id, 'success': True})

@app.route('/api/veiculos-relevantes/<int:vr_id>', methods=['PUT'])
def update_veiculo_relevante(vr_id):
    data = request.json
    db.update_veiculo_relevante(
        vr_id=vr_id,
        nome=data['nome'],
        dominio=data['dominio'],
        ativo=data.get('ativo', True)
    )
    return jsonify({'success': True})

@app.route('/api/veiculos-relevantes/<int:vr_id>', methods=['DELETE'])
def delete_veiculo_relevante(vr_id):
    db.delete_veiculo_relevante(vr_id)
    return jsonify({'success': True})

# API - Veículos de Nicho
@app.route('/api/veiculos-nicho', methods=['GET'])
def get_veiculos_nicho():
    veiculos = db.get_veiculos_nicho()
    return jsonify(veiculos)

@app.route('/api/veiculos-nicho', methods=['POST'])
def create_veiculo_nicho():
    data = request.json
    vn_id = db.create_veiculo_nicho(
        nome=data['nome'],
        dominio=data['dominio'],
        categoria=data.get('categoria'),
        ativo=data.get('ativo', True)
    )
    return jsonify({'id': vn_id, 'success': True})

@app.route('/api/veiculos-nicho/<int:vn_id>', methods=['PUT'])
def update_veiculo_nicho(vn_id):
    data = request.json
    db.update_veiculo_nicho(
        vn_id=vn_id,
        nome=data['nome'],
        dominio=data['dominio'],
        categoria=data.get('categoria'),
        ativo=data.get('ativo', True)
    )
    return jsonify({'success': True})

@app.route('/api/veiculos-nicho/<int:vn_id>', methods=['DELETE'])
def delete_veiculo_nicho(vn_id):
    db.delete_veiculo_nicho(vn_id)
    return jsonify({'success': True})

# API - Configurações
@app.route('/api/configuracoes', methods=['GET'])
def get_configuracoes():
    configs = db.get_configuracoes()
    return jsonify(configs)

@app.route('/api/configuracoes', methods=['PUT'])
def update_configuracoes():
    data = request.json
    for chave, valor in data.items():
        db.update_configuracao(chave, str(valor))
    return jsonify({'success': True})

# API - Brandwatch Config
@app.route('/api/brandwatch-config', methods=['GET'])
def get_brandwatch_config():
    config = db.get_brandwatch_config()
    if config:
        # Não retornar senha
        config['password'] = '***'
    return jsonify(config)

@app.route('/api/brandwatch-config', methods=['POST'])
def save_brandwatch_config():
    data = request.json
    db.save_brandwatch_config(
        email=data['email'],
        password=data['password'],
        project=data['project'],
        query_name=data['query_name']
    )
    return jsonify({'success': True})

# API - Análises
@app.route('/api/analises', methods=['GET'])
def get_analises():
    analises = db.get_analises()
    return jsonify(analises)

@app.route('/api/analises/<int:analise_id>', methods=['GET'])
def get_analise(analise_id):
    analise = db.get_analise(analise_id)
    if not analise:
        return jsonify({'error': 'Análise não encontrada'}), 404
    
    # Buscar resultados IEDI
    resultados = db.get_resultados_iedi(analise_id)
    analise['resultados'] = resultados
    
    return jsonify(analise)

@app.route('/api/analises/<int:analise_id>/mencoes', methods=['GET'])
def get_analise_mencoes(analise_id):
    banco_id = request.args.get('banco_id', type=int)
    mencoes = db.get_mencoes(analise_id, banco_id)
    return jsonify(mencoes)

@app.route('/api/analises/executar', methods=['POST'])
def executar_analise():
    """
    Executa uma análise IEDI
    Espera receber menções já extraídas da Brandwatch
    """
    data = request.json
    data_inicio = data['data_inicio']
    data_fim = data['data_fim']
    mencoes = data['mencoes']  # Lista de menções da Brandwatch
    
    try:
        # Criar análise
        analise_id = db.create_analise(data_inicio, data_fim)
        
        # Filtrar apenas menções de imprensa
        mencoes_imprensa = [
            m for m in mencoes
            if m.get('contentSourceName') == 'News' or 
               'news' in str(m.get('contentSource', '')).lower()
        ]
        
        # Calcular IEDI
        calculadora = CalculadoraIEDI(db)
        
        # Agrupar menções por banco
        mencoes_por_banco = {}
        bancos = db.get_bancos(ativo_only=True)
        
        for mencao in mencoes_imprensa:
            texto = f"{mencao.get('title', '')} {mencao.get('snippet', '')}"
            banco_identificado = calculadora.identificar_banco(texto)
            
            if banco_identificado:
                if banco_identificado not in mencoes_por_banco:
                    mencoes_por_banco[banco_identificado] = []
                mencoes_por_banco[banco_identificado].append(mencao)
        
        # Calcular IEDI para cada banco
        resultados_bancos = []
        
        for banco in bancos:
            banco_nome = banco['nome']
            banco_id = banco['id']
            mencoes_banco = mencoes_por_banco.get(banco_nome, [])
            
            resultado = calculadora.calcular_iedi_banco(mencoes_banco, banco_nome, banco_id)
            resultados_bancos.append(resultado)
            
            # Salvar menções no banco
            for i, mencao_data in enumerate(resultado['resultados']):
                mencao_original = mencoes_banco[i] if i < len(mencoes_banco) else {}
                
                db.save_mencao({
                    'analise_id': analise_id,
                    'banco_id': banco_id,
                    'mention_id': mencao_original.get('id'),
                    'titulo': mencao_original.get('title'),
                    'snippet': mencao_original.get('snippet'),
                    'url': mencao_original.get('url'),
                    'domain': mencao_original.get('domain'),
                    'sentiment': mencao_data['sentiment'],
                    'monthly_visitors': mencao_original.get('monthlyVisitors', 0),
                    'data_mencao': mencao_original.get('date'),
                    'nota': mencao_data['nota'],
                    'grupo_alcance': mencao_data['grupo_alcance'],
                    'variaveis': mencao_data['variaveis']
                })
        
        # Calcular IEDI final com balizamento
        resultados_finais = calculadora.calcular_iedi_final_com_balizamento(resultados_bancos)
        
        # Salvar resultados
        for resultado in resultados_finais:
            db.save_resultado_iedi(analise_id, resultado['banco_id'], resultado)
        
        # Atualizar status da análise
        db.update_analise_status(
            analise_id=analise_id,
            status='concluida',
            total_mencoes=len(mencoes_imprensa)
        )
        
        return jsonify({
            'success': True,
            'analise_id': analise_id,
            'total_mencoes': len(mencoes_imprensa),
            'resultados': resultados_finais
        })
    
    except Exception as e:
        # Atualizar status com erro
        if 'analise_id' in locals():
            db.update_analise_status(
                analise_id=analise_id,
                status='erro',
                mensagem_erro=str(e)
            )
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API - Seed inicial de dados
@app.route('/api/seed', methods=['POST'])
def seed_data():
    """Popula o banco com dados iniciais"""
    try:
        # Bancos
        bancos_iniciais = [
            {'nome': 'Banco do Brasil', 'variacoes': ['banco do brasil', 'bb', 'banco do brazil']},
            {'nome': 'Itaú', 'variacoes': ['itaú', 'itau', 'banco itaú', 'banco itau']},
            {'nome': 'Bradesco', 'variacoes': ['bradesco', 'banco bradesco']},
            {'nome': 'Santander', 'variacoes': ['santander', 'banco santander']},
        ]
        
        for banco_data in bancos_iniciais:
            try:
                db.create_banco(banco_data['nome'], banco_data['variacoes'])
            except:
                pass  # Já existe
        
        # Veículos relevantes (amostra)
        veiculos_relevantes = [
            ('G1', 'g1.globo.com'),
            ('Folha de S. Paulo', 'folha.uol.com.br'),
            ('Estadão', 'estadao.com.br'),
            ('O Globo', 'oglobo.globo.com'),
            ('UOL', 'uol.com.br'),
            ('Valor Econômico', 'valor.globo.com'),
            ('Exame', 'exame.com'),
            ('InfoMoney', 'infomoney.com.br'),
        ]
        
        for nome, dominio in veiculos_relevantes:
            try:
                db.create_veiculo_relevante(nome, dominio)
            except:
                pass
        
        # Veículos de nicho
        veiculos_nicho = [
            ('InfoMoney', 'infomoney.com.br', 'Finanças'),
            ('Money Times', 'moneytimes.com.br', 'Finanças'),
            ('Valor Investe', 'valorinveste.globo.com', 'Investimentos'),
            ('E-Investidor', 'einvestidor.estadao.com.br', 'Investimentos'),
        ]
        
        for nome, dominio, categoria in veiculos_nicho:
            try:
                db.create_veiculo_nicho(nome, dominio, categoria)
            except:
                pass
        
        return jsonify({'success': True, 'message': 'Dados iniciais inseridos'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Criar diretório de dados se não existir
    os.makedirs('data', exist_ok=True)
    
    # Executar aplicação
    app.run(host='0.0.0.0', port=5000, debug=True)
