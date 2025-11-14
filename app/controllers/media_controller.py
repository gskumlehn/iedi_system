from flask import Blueprint, render_template, request, jsonify
from app.models import Database

media_bp = Blueprint("media", __name__)
db = Database()

# Veículos Relevantes
@media_bp.route("/relevantes")
def relevant_media():
    """Página de gerenciamento de veículos relevantes"""
    return render_template("veiculos_relevantes.html")

@media_bp.route("/api/relevantes", methods=['GET'])
def get_veiculos_relevantes():
    """Listar veículos relevantes"""
    veiculos = db.get_veiculos_relevantes()
    return jsonify(veiculos)

@media_bp.route("/api/relevantes", methods=['POST'])
def create_veiculo_relevante():
    """Criar veículo relevante"""
    data = request.json
    vr_id = db.create_veiculo_relevante(
        nome=data['nome'],
        dominio=data['dominio'],
        ativo=data.get('ativo', True)
    )
    return jsonify({'id': vr_id, 'success': True})

@media_bp.route("/api/relevantes/<int:vr_id>", methods=['PUT'])
def update_veiculo_relevante(vr_id):
    """Atualizar veículo relevante"""
    data = request.json
    db.update_veiculo_relevante(
        vr_id=vr_id,
        nome=data['nome'],
        dominio=data['dominio'],
        ativo=data.get('ativo', True)
    )
    return jsonify({'success': True})

@media_bp.route("/api/relevantes/<int:vr_id>", methods=['DELETE'])
def delete_veiculo_relevante(vr_id):
    """Excluir veículo relevante"""
    db.delete_veiculo_relevante(vr_id)
    return jsonify({'success': True})

# Veículos de Nicho
@media_bp.route("/nicho")
def niche_media():
    """Página de gerenciamento de veículos de nicho"""
    return render_template("veiculos_nicho.html")

@media_bp.route("/api/nicho", methods=['GET'])
def get_veiculos_nicho():
    """Listar veículos de nicho"""
    veiculos = db.get_veiculos_nicho()
    return jsonify(veiculos)

@media_bp.route("/api/nicho", methods=['POST'])
def create_veiculo_nicho():
    """Criar veículo de nicho"""
    data = request.json
    vn_id = db.create_veiculo_nicho(
        nome=data['nome'],
        dominio=data['dominio'],
        categoria=data.get('categoria'),
        ativo=data.get('ativo', True)
    )
    return jsonify({'id': vn_id, 'success': True})

@media_bp.route("/api/nicho/<int:vn_id>", methods=['PUT'])
def update_veiculo_nicho(vn_id):
    """Atualizar veículo de nicho"""
    data = request.json
    db.update_veiculo_nicho(
        vn_id=vn_id,
        nome=data['nome'],
        dominio=data['dominio'],
        categoria=data.get('categoria'),
        ativo=data.get('ativo', True)
    )
    return jsonify({'success': True})

@media_bp.route("/api/nicho/<int:vn_id>", methods=['DELETE'])
def delete_veiculo_nicho(vn_id):
    """Excluir veículo de nicho"""
    db.delete_veiculo_nicho(vn_id)
    return jsonify({'success': True})
