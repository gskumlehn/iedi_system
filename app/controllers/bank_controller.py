from flask import Blueprint, render_template, request, jsonify
from app.repositories.bank_repository import BankRepository

bank_bp = Blueprint("bank", __name__)

@bank_bp.route("/")
def index():
    return render_template("banks.html")

@bank_bp.route("/api", methods=['GET'])
def list_banks():
    banks = BankRepository.list_all()
    return jsonify(banks)

@bank_bp.route("/api", methods=['POST'])
def create_bank():
    data = request.json
    bank_id = BankRepository.create(
        name=data['name'],
        variations=data['variations'],
        active=data.get('active', True)
    )
    return jsonify({'id': bank_id, 'success': True})

@bank_bp.route("/api/<int:bank_id>", methods=['PUT'])
def update_bank(bank_id):
    data = request.json
    BankRepository.update(
        bank_id=bank_id,
        name=data['name'],
        variations=data['variations'],
        active=data.get('active', True)
    )
    return jsonify({'success': True})

@bank_bp.route("/api/<int:bank_id>", methods=['DELETE'])
def delete_bank(bank_id):
    BankRepository.delete(bank_id)
    return jsonify({'success': True})
