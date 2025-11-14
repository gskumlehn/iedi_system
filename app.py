"""
Sistema IEDI - Aplicação Flask Principal
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from app.models import Database
from app.iedi_calculator_brandwatch import criar_calculadora_brandwatch
from app.brandwatch_service import create_brandwatch_service, BRANDWATCH_AVAILABLE
import json
import os
import logging
from datetime import datetime

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar banco de dados
db = Database()

# Rotas de páginas HTML
@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/bancos')
def banks():
    return render_template('bancos.html')

@app.route('/porta-vozes')
def porta_vozes_page():
    return render_template('porta_vozes.html')

@app.route('/veiculos-relevantes')
def relevant_media():
    return render_template('veiculos_relevantes.html')

@app.route('/veiculos-nicho')
def niche_media():
    return render_template('veiculos_nicho.html')

@app.route('/configuracoes')
def configuracoes_page():
    return render_template('configuracoes.html')

@app.route('/analises')
def analyses():
    return render_template('analises.html')

@app.route('/analise-resultados')
def analise_resultados_page():
    return render_template('analise_resultados.html')

@app.route('/analise/<int:analise_id>')
def analise_detalhes_page(analise_id):
    return render_template('analise_detalhes.html', analise_id=analise_id)

@app.route('/executar-analise')
def executar_analise_page():
    return render_template('executar_analise.html')

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
        calculadora = criar_calculadora_brandwatch(db)
        
        # Agrupar menções por banco
        mencoes_por_banco = {}
        bancos = db.get_bancos(ativo_only=True)
        
        for mencao in mencoes_imprensa:
            texto = f"{mencao.get('title', '')} {mencao.get('snippet', '')}"
            # Banco identificado via categoryDetail da Brandwatch
            
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
            
            resultado = calculadora.calcular_iedi_banco(mencoes_banco, banco_nome, banco.get("variacoes", []))
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
        # Balizamento já aplicado na nova calculadora
        resultados_finais = calculadora.calcular_iedi_comparativo([r["resultado"] for r in resultados_bancos])
        
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

# API - Brandwatch Integration
@app.route('/api/brandwatch/status', methods=['GET'])
def brandwatch_status():
    """Verifica se a integração Brandwatch está disponível"""
    config = db.get_brandwatch_config()
    return jsonify({
        'available': BRANDWATCH_AVAILABLE,
        'configured': config is not None
    })

@app.route('/api/brandwatch/extrair', methods=['POST'])
def brandwatch_extrair():
    """Extrai menções da Brandwatch e executa análise IEDI"""
    if not BRANDWATCH_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Brandwatch API não está disponível. Instale bcr-api.'
        }), 400
    
    data = request.json
    data_inicio = data.get('data_inicio')
    data_fim = data.get('data_fim')
    query_name = data.get('query_name')
    
    if not all([data_inicio, data_fim]):
        return jsonify({
            'success': False,
            'error': 'data_inicio e data_fim são obrigatórios'
        }), 400
    
    try:
        # Buscar configuração Brandwatch
        config = db.get_brandwatch_config()
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuração Brandwatch não encontrada'
            }), 400
        
        # Usar query_name da request ou da config
        query = query_name or config['query_name']
        
        logger.info(f"Iniciando extração Brandwatch: {data_inicio} a {data_fim}")
        
        # Criar serviço Brandwatch
        bw_service = create_brandwatch_service(config)
        if not bw_service:
            return jsonify({
                'success': False,
                'error': 'Erro ao criar serviço Brandwatch'
            }), 500
        
        # Extrair menções
        mencoes = bw_service.extract_mentions_by_date_range(
            query_name=query,
            start_date_str=data_inicio,
            end_date_str=data_fim
        )
        
        logger.info(f"Extraídas {len(mencoes)} menções da Brandwatch")
        
        # Filtrar apenas imprensa
        mencoes_imprensa = bw_service.filter_news_mentions(mencoes)
        
        logger.info(f"Filtradas {len(mencoes_imprensa)} menções de imprensa")
        
        if len(mencoes_imprensa) == 0:
            return jsonify({
                'success': False,
                'error': 'Nenhuma menção de imprensa encontrada no período'
            }), 400
        
        # Executar análise IEDI
        analise_id = db.create_analise(data_inicio, data_fim)
        
        calculadora = criar_calculadora_brandwatch(db)
        
        # Agrupar menções por banco
        mencoes_por_banco = {}
        bancos = db.get_bancos(ativo_only=True)
        
        for mencao in mencoes_imprensa:
            texto = f"{mencao.get('title', '')} {mencao.get('snippet', '')}"
            # Banco identificado via categoryDetail da Brandwatch
            
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
            
            resultado = calculadora.calcular_iedi_banco(mencoes_banco, banco_nome, banco.get("variacoes", []))
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
        # Balizamento já aplicado na nova calculadora
        resultados_finais = calculadora.calcular_iedi_comparativo([r["resultado"] for r in resultados_bancos])
        
        # Salvar resultados
        for resultado in resultados_finais:
            db.save_resultado_iedi(analise_id, resultado['banco_id'], resultado)
        
        # Atualizar status da análise
        db.update_analise_status(
            analise_id=analise_id,
            status='concluida',
            total_mencoes=len(mencoes_imprensa)
        )
        
        logger.info(f"Análise concluída. ID: {analise_id}")
        
        return jsonify({
            'success': True,
            'analise_id': analise_id,
            'total_mencoes': len(mencoes_imprensa),
            'total_mencoes_brutas': len(mencoes),
            'resultados': resultados_finais
        })
    
    except Exception as e:
        logger.error(f"Erro na extração Brandwatch: {str(e)}")
        
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




@app.route('/api/analises/executar-resultados', methods=['POST'])
def executar_analise_resultados():
    """Executa análise IEDI de resultados com períodos diferentes por banco"""
    if not BRANDWATCH_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Brandwatch API não está disponível. Instale bcr-api.'
        }), 400
    
    data = request.json
    periodo_referencia = data.get('periodo_referencia')
    bancos_periodos = data.get('bancos', [])
    query_name = data.get('query_name')
    
    if not periodo_referencia:
        return jsonify({
            'success': False,
            'error': 'periodo_referencia é obrigatório'
        }), 400
    
    if not bancos_periodos or len(bancos_periodos) == 0:
        return jsonify({
            'success': False,
            'error': 'Defina períodos para pelo menos um banco'
        }), 400
    
    try:
        # Buscar configuração Brandwatch
        config = db.get_brandwatch_config()
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuração Brandwatch não encontrada'
            }), 400
        
        # Usar query_name da request ou da config
        query = query_name or config['query_name']
        
        logger.info(f"Iniciando análise de resultados: {periodo_referencia}")
        
        # Criar análise
        analise_id = db.create_analise(
            periodo_referencia=periodo_referencia,
            tipo='resultados'
        )
        
        # Criar serviço Brandwatch
        bw_service = create_brandwatch_service(config)
        if not bw_service:
            return jsonify({
                'success': False,
                'error': 'Erro ao criar serviço Brandwatch'
            }), 500
        
        calculadora = criar_calculadora_brandwatch(db)
        
        # Processar cada banco
        total_mencoes_geral = 0
        periodos_info = []
        mencoes_por_banco = {}
        
        for banco_periodo in bancos_periodos:
            banco_id = banco_periodo['banco_id']
            banco_nome = banco_periodo['banco_nome']
            data_divulgacao = banco_periodo['data_divulgacao']
            dias_coleta = banco_periodo['dias_coleta']
            
            # Calcular data_fim
            from datetime import datetime, timedelta
            data_div_obj = datetime.strptime(data_divulgacao, '%Y-%m-%d')
            data_fim_obj = data_div_obj + timedelta(days=dias_coleta)
            data_fim = data_fim_obj.strftime('%Y-%m-%d')
            
            logger.info(f"Processando {banco_nome}: {data_divulgacao} a {data_fim}")
            
            # Extrair menções para este período
            mencoes = bw_service.extract_mentions_by_date_range(
                query_name=query,
                start_date_str=data_divulgacao,
                end_date_str=data_fim
            )
            
            logger.info(f"Extraídas {len(mencoes)} menções para {banco_nome}")
            
            # Filtrar apenas imprensa
            mencoes_imprensa = bw_service.filter_news_mentions(mencoes)
            
            # Filtrar por categoryDetail (nome do banco)
            mencoes_banco = bw_service.filter_by_category_detail(mencoes_imprensa, banco_nome)
            
            logger.info(f"Filtradas {len(mencoes_banco)} menções de {banco_nome}")
            
            # Salvar período no banco
            periodo_id = db.create_periodo_banco(
                analise_id=analise_id,
                banco_id=banco_id,
                data_divulgacao=data_divulgacao,
                data_inicio=data_divulgacao,
                data_fim=data_fim,
                dias_coleta=dias_coleta
            )
            
            # Atualizar total de menções do período
            db.update_periodo_banco_mencoes(periodo_id, len(mencoes_banco))
            
            # Armazenar menções para cálculo posterior
            mencoes_por_banco[banco_id] = mencoes_banco
            total_mencoes_geral += len(mencoes_banco)
            
            periodos_info.append({
                'banco_id': banco_id,
                'banco_nome': banco_nome,
                'data_divulgacao': data_divulgacao,
                'data_inicio': data_divulgacao,
                'data_fim': data_fim,
                'total_mencoes': len(mencoes_banco)
            })
        
        logger.info(f"Total de menções coletadas: {total_mencoes_geral}")
        
        # Calcular IEDI para cada banco
        resultados_bancos = []
        
        for banco_id, mencoes_banco in mencoes_por_banco.items():
            if len(mencoes_banco) == 0:
                continue
            
            banco = db.get_banco(banco_id)
            
            # Calcular IEDI
            resultado = calculadora.calcular_iedi_banco(
                banco_id=banco_id,
                mencoes=mencoes_banco
            )
            
            # Salvar menções no banco
            for mencao_calc in resultado['mencoes_detalhadas']:
                mencao_dict = {
                    'analise_id': analise_id,
                    'banco_id': banco_id,
                    'mention_id': mencao_calc.get('mention_id'),
                    'titulo': mencao_calc.get('titulo'),
                    'snippet': mencao_calc.get('snippet'),
                    'url': mencao_calc.get('url'),
                    'domain': mencao_calc.get('domain'),
                    'sentiment': mencao_calc.get('sentiment'),
                    'category_detail': mencao_calc.get('category_detail'),
                    'monthly_visitors': mencao_calc.get('monthly_visitors', 0),
                    'data_mencao': mencao_calc.get('data_mencao'),
                    'nota': mencao_calc.get('nota', 0),
                    'grupo_alcance': mencao_calc.get('grupo_alcance'),
                    'variaveis': mencao_calc.get('variaveis', {})
                }
                db.save_mencao(mencao_dict)
            
            resultados_bancos.append({
                'banco_id': banco_id,
                'banco': banco['nome'],
                'resultado': resultado
            })
        
        # Aplicar balizamento final
        resultados_finais = calculadora.calcular_iedi_final_com_balizamento(
            [r['resultado'] for r in resultados_bancos]
        )
        
        # Salvar resultados
        for i, resultado_final in enumerate(resultados_finais):
            banco_id = resultados_bancos[i]['banco_id']
            db.save_resultado_iedi(analise_id, banco_id, resultado_final)
        
        # Atualizar status da análise
        db.update_analise_status(
            analise_id=analise_id,
            status='concluida',
            total_mencoes=total_mencoes_geral
        )
        
        # Preparar resposta
        resultados_response = []
        for resultado in resultados_finais:
            resultados_response.append({
                'banco': resultado['banco'],
                'iedi_final': resultado['iedi_final'],
                'iedi_medio': resultado['iedi_medio'],
                'volume_total': resultado['volume_total'],
                'positividade': resultado['positividade']
            })
        
        return jsonify({
            'success': True,
            'analise_id': analise_id,
            'periodo_referencia': periodo_referencia,
            'total_mencoes': total_mencoes_geral,
            'periodos': periodos_info,
            'resultados': resultados_response
        })
    
    except Exception as e:
        logger.error(f"Erro na análise de resultados: {str(e)}")
        
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
        
        # Veículos relevantes (lista completa)
        veiculos_relevantes = [
            ('Agência Brasil', 'agenciabrasil.ebc.com.br'),
            ('Band', 'band.uol.com.br'),
            ('BandNews', 'bandnewstv.com.br'),
            ('BBC Brasil', 'bbc.com/portuguese'),
            ('Bloomberg', 'bloomberg.com.br'),
            ('Bloomberg Línea', 'bloomberglinea.com.br'),
            ('Brasil 247', 'brasil247.com'),
            ('Carta Capital', 'cartacapital.com.br'),
            ('CNN Brasil', 'cnnbrasil.com.br'),
            ('Correio Braziliense', 'correiobraziliense.com.br'),
            ('E-Investidor', 'einvestidor.estadao.com.br'),
            ('Época Negócios', 'epocanegocios.globo.com'),
            ('Estadão', 'estadao.com.br'),
            ('Exame', 'exame.com'),
            ('Folha de S. Paulo', 'folha.uol.com.br'),
            ('Forbes Brasil', 'forbes.com.br'),
            ('G1', 'g1.globo.com'),
            ('Globo News', 'globonews.globo.com'),
            ('Globo Rural', 'globorural.globo.com'),
            ('InfoMoney', 'infomoney.com.br'),
            ('IstoÉ', 'istoe.com.br'),
            ('IstoÉ Dinheiro', 'istoedinheiro.com.br'),
            ('Jovem Pan', 'jovempan.com.br'),
            ('Metrópoles', 'metropoles.com'),
            ('Money Times', 'moneytimes.com.br'),
            ('O Antagonista', 'oantagonista.com'),
            ('O Globo', 'oglobo.globo.com'),
            ('Poder 360', 'poder360.com.br'),
            ('R7', 'r7.com'),
            ('Reuters', 'reuters.com'),
            ('Revista Piauí', 'revistapiaui.com.br'),
            ('Safras & Mercado', 'safras.com.br'),
            ('Seu Dinheiro', 'seudinheiro.com'),
            ('Terra', 'terra.com.br'),
            ('CNBC', 'cnbc.com'),
            ('TV Globo', 'globo.com'),
            ('UOL', 'uol.com.br'),
            ('Valor Econômico', 'valor.globo.com'),
            ('Valor Investe', 'valorinveste.globo.com'),
            ('Veja', 'veja.abril.com.br'),
        ]
        
        for nome, dominio in veiculos_relevantes:
            try:
                db.create_veiculo_relevante(nome, dominio)
            except:
                pass
        
        # Veículos de nicho (lista completa com acessos mensais)
        veiculos_nicho = [
            ('Agência Pública', 'apublica.org', 420000),
            ('Agência Spotlight', 'agenciaspotlight.com.br', 50000),
            ('AzMina', 'azmina.com.br', 50000),
            ('Capital Digital', 'capitaldigital.com.br', 50000),
            ('Congresso em Foco', 'congressoemfoco.uol.com.br', 3000000),
            ('Época Negócios', 'epocanegocios.globo.com', 6000000),
            ('Forbes Brasil', 'forbes.com.br', 2000000),
            ('Globo News', 'globonews.globo.com', 313000000),
            ('Globo Rural', 'globorural.globo.com', 150000),
            ('InfoMoney', 'infomoney.com.br', 23000000),
            ('Investing.com', 'br.investing.com', 159000000),
            ('IstoÉ Dinheiro', 'istoedinheiro.com.br', 3000000),
            ('Le Monde Diplomatique Brasil', 'diplomatique.org.br', 260000000),
            ('MoneyTimes', 'moneytimes.com.br', 8000000),
            ('Pequenas Empresas, Grandes Negócios', 'revistapegn.globo.com', 2000000),
            ('Poder 360', 'poder360.com.br', 23000000),
            ('Repórter Brasil', 'reporterbrasil.org.br', 190000),
            ('Seu Dinheiro', 'seudinheiro.com', 3000000),
            ('The Brazilian Report', 'brazilian.report', 210000),
            ('The Intercept', 'theintercept.com/brasil', 5000000),
            ('Valor Econômico', 'valor.globo.com', 14000000),
            ('Valor Investe', 'valorinveste.globo.com', 6000000),
        ]
        
        for nome, dominio, monthly_visitors in veiculos_nicho:
            try:
                # Determinar categoria baseado no grupo de alcance
                if monthly_visitors >= 29000001:
                    categoria = 'Grupo A'
                elif 11000001 <= monthly_visitors <= 29000000:
                    categoria = 'Grupo B'
                elif 500000 <= monthly_visitors <= 11000000:
                    categoria = 'Grupo C'
                else:
                    categoria = 'Grupo D'
                
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
