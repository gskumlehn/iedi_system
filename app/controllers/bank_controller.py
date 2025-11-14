from flask import Blueprint, render_template, request, jsonify
from app.repositories.bank_repository import BankRepository

bank_bp = Blueprint("bank", __name__)

@bank_bp.route("/")
def index():
    """Página de gerenciamento de bancos"""
    return render_template("bancos.html")

@bank_bp.route("/api", methods=['GET'])
def get_bancos():
    """Listar todos os bancos"""
    bancos = BankRepository.list_all()
    return jsonify(bancos)

@bank_bp.route("/api", methods=['POST'])
def create_banco():
    """Criar novo banco"""
    data = request.json
    banco_id = BankRepository.create(
        name=data['nome'],
        variations=data['variacoes'],
        active=data.get('ativo', True)
    )
    return jsonify({'id': banco_id, 'success': True})

@bank_bp.route("/api/<int:banco_id>", methods=['PUT'])
def update_banco(banco_id):
    """Atualizar banco existente"""
    data = request.json
    BankRepository.update(
        bank_id=banco_id,
        name=data['nome'],
        variations=data['variacoes'],
        active=data.get('ativo', True)
    )
    return jsonify({'success': True})

@bank_bp.route("/api/<int:banco_id>", methods=['DELETE'])
def delete_banco(banco_id):
    """Excluir banco"""
    BankRepository.delete(banco_id)
    return jsonify({'success': True})
