from app.services.analysis_service import AnalysisService
from flask import Blueprint, jsonify, request

analysis_bp = Blueprint("analysis", __name__)
analysis_service = AnalysisService()

@analysis_bp.route("/api", methods=['POST'])
def create_analysis():
    try:
        data = request.get_json()

        name = data.get("name")
        query = data.get("query")
        bank_names = data.get("bank_names", [])
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        custom_bank_dates = data.get("custom_bank_dates", [])

        analysis = analysis_service.save(
            name=name,
            query=query,
            bank_names=bank_names,
            start_date=start_date,
            end_date=end_date,
            custom_bank_dates=custom_bank_dates
        )

        return jsonify({"message": "Análise criada com sucesso."}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
