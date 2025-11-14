from flask import Blueprint, render_template, request, jsonify
from app.models import Database

analysis_bp = Blueprint("analysis", __name__)
db = Database()

@analysis_bp.route("/")
def index():
    """Página de visualização de análises"""
    return render_template("analises.html")

@analysis_bp.route("/api", methods=['GET'])
def get_analises():
    """Listar todas as análises"""
    analises = db.get_analises()
    return jsonify(analises)

@analysis_bp.route("/api/<int:analise_id>", methods=['GET'])
def get_analise(analise_id):
    """Obter detalhes de uma análise específica"""
    analise = db.get_analise(analise_id)
    if not analise:
        return jsonify({'error': 'Análise não encontrada'}), 404
    
    # Buscar resultados IEDI
    resultados = db.get_resultados_iedi(analise_id)
    analise['resultados'] = resultados
    
    return jsonify(analise)

@analysis_bp.route("/api/<int:analise_id>/mencoes", methods=['GET'])
def get_analise_mencoes(analise_id):
    """Obter menções de uma análise"""
    banco_id = request.args.get('banco_id', type=int)
    mencoes = db.get_mencoes(analise_id, banco_id)
    return jsonify(mencoes)
