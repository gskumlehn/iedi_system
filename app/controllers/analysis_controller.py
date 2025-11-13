from flask import Blueprint, jsonify, request
from app.services.analysis_service import AnalysisService
from app.services.bank_service import BankService

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/analysis")
analysis_service = AnalysisService()
bank_service = BankService()

@analysis_bp.route("/", methods=["POST"])
def create_analysis():
    try:
        data = request.json
        result = analysis_service.create_analysis(
            name=data["name"],
            query=data["query"],
            custom_period=data.get("custom_period", False),
            bank_periods=data.get("bank_periods", [])
        )
        return jsonify({"success": True, "message": "Análise criada com sucesso", "data": result}), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao criar análise: {str(e)}"}), 500

@analysis_bp.route("/", methods=["GET"])
def list_analyses():
    try:
        analyses = analysis_service.get_all_analyses()
        return jsonify({"success": True, "data": analyses}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao listar análises: {str(e)}"}), 500

@analysis_bp.route("/<int:analysis_id>", methods=["GET"])
def get_analysis(analysis_id):
    try:
        result = analysis_service.get_analysis_results(analysis_id)
        if not result:
            return jsonify({"success": False, "message": "Análise não encontrada"}), 404
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao buscar análise: {str(e)}"}), 500

@analysis_bp.route("/<int:analysis_id>/process", methods=["POST"])
def process_mentions(analysis_id):
    try:
        data = request.json
        result = analysis_service.process_mentions(analysis_id, data["mentions_by_bank"])
        return jsonify({"success": True, "message": "Menções processadas com sucesso", "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao processar menções: {str(e)}"}), 500

@analysis_bp.route("/banks", methods=["GET"])
def get_banks():
    try:
        banks = bank_service.get_all_active()
        return jsonify({"success": True, "data": banks}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao buscar bancos: {str(e)}"}), 500
