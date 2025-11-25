from app.services.analysis_service import AnalysisService
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.bank_analysis_repository import BankAnalysisRepository
from app.repositories.bank_repository import BankRepository
from flask import Blueprint, jsonify, request

analysis_bp = Blueprint("analysis", __name__)
analysis_service = AnalysisService()

@analysis_bp.route("/api/analyses", methods=['GET'])
def list_analyses():
    try:
        analyses = AnalysisRepository.find_all()
        return jsonify({
            "analyses": [
                {
                    "id": a.id,
                    "name": a.name,
                    "query_name": a.query_name,
                    "status": a.status.name if hasattr(a.status, 'name') else str(a.status),
                    "is_custom_dates": a.is_custom_dates,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in analyses
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/api/analyses/<analysis_id>", methods=['GET'])
def get_analysis(analysis_id):
    try:
        analysis = AnalysisRepository.find_by_id(analysis_id)
        if not analysis:
            return jsonify({"error": "Análise não encontrada"}), 404
        return jsonify({
            "analysis": {
                "id": analysis.id,
                "name": analysis.name,
                "query_name": analysis.query_name,
                "status": analysis.status.name if hasattr(analysis.status, 'name') else str(analysis.status),
                "is_custom_dates": analysis.is_custom_dates,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            }
        }), 200
    except ValueError as e:
        return jsonify({"error": f"ID inválido: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/api/analyses/<analysis_id>/banks", methods=['GET'])
def get_bank_analyses(analysis_id):
    try:
        analysis = AnalysisRepository.find_by_id(analysis_id)
        if not analysis:
            return jsonify({"error": "Análise não encontrada"}), 404
        bank_analyses = BankAnalysisRepository.find_by_analysis_id(analysis_id)
        return jsonify({
            "bank_analyses": [
                {
                    "id": ba.id,
                    "analysis_id": ba.analysis_id,
                    "bank_name": ba.bank_name.name if hasattr(ba.bank_name, 'name') else str(ba.bank_name),
                    "start_date": ba.start_date.isoformat() if ba.start_date else None,
                    "end_date": ba.end_date.isoformat() if ba.end_date else None,
                    "total_mentions": ba.total_mentions or 0,
                    "positive_volume": ba.positive_volume or 0.0,
                    "negative_volume": ba.negative_volume or 0.0,
                    "iedi_mean": ba.iedi_mean,
                    "iedi_score": ba.iedi_score,
                }
                for ba in bank_analyses
            ]
        }), 200
    except ValueError as e:
        return jsonify({"error": f"ID inválido: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/api/analyses", methods=['POST'])
def create_analysis():
    try:
        data = request.get_json()
        name = data.get("name")
        query_name = "BB | Monitoramento | + Lagos"
        parent_name = "Análise de Resultado - Bancos"
        bank_names = data.get("bank_names", [])
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        custom_bank_dates = data.get("custom_bank_dates", [])
        analysis = analysis_service.save(
            name=name,
            query_name=query_name,
            parent_name=parent_name,
            bank_names=bank_names,
            start_date=start_date,
            end_date=end_date,
            custom_bank_dates=custom_bank_dates
        )
        return jsonify({
            "message": "Análise criada com sucesso.",
            "analysis": {
                "id": analysis.id,
                "name": analysis.name,
                "query_name": analysis.query_name,
                "status": analysis.status.name if hasattr(analysis.status, 'name') else str(analysis.status),
                "is_custom_dates": analysis.is_custom_dates,
            }
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/api/banks", methods=['GET'])
def list_banks():
    try:
        banks = BankRepository.find_all()
        return jsonify({
            "banks": [
                {
                    "id": b.id,
                    "name": b.name.name if hasattr(b.name, 'name') else str(b.name),
                    "display_name": b.display_name,
                    "variations": b.variations if hasattr(b, 'variations') else [],
                }
                for b in banks
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/api/analyses/<analysis_id>/restart", methods=['POST'])
def restart_analysis(analysis_id):
    try:
        analysis = AnalysisRepository.find_by_id(analysis_id)
        if not analysis:
            return jsonify({"error": "Análise não encontrada"}), 404

        bank_analyses = BankAnalysisRepository.find_by_analysis_id(analysis_id)
        if not bank_analyses:
            return jsonify({"error": "Nenhuma análise de banco encontrada para esta análise"}), 404

        parent_name = "Análise de Resultado - Bancos"

        analysis_service.process_and_update_status(analysis, bank_analyses, parent_name)
        return jsonify({"message": "Processamento reiniciado com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
