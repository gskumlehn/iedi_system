from app.services.analysis_service import AnalysisService
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.bank_analysis_repository import BankAnalysisRepository
from app.repositories.bank_repository import BankRepository
from flask import Blueprint, jsonify, request

analysis_bp = Blueprint("analysis", __name__)
analysis_service = AnalysisService()

# ============================================================================
# ENDPOINTS
# ============================================================================

@analysis_bp.route("/api/analyses", methods=['GET'])
def list_analyses():
    """
    Lista todas as análises criadas.
    
    Returns:
        JSON com lista de análises ordenadas por data de criação (mais recente primeiro)
    
    Regras de Negócio:
        - Retornar lista vazia se não houver análises (não erro)
        - Ordenar por created_at DESC
    """
    try:
        # TODO: Implementar AnalysisRepository.find_all()
        # analyses = AnalysisRepository.find_all()
        
        # Placeholder - remover quando implementar find_all()
        analyses = []
        
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
    """
    Busca uma análise específica por ID.
    
    Args:
        analysis_id: UUID da análise
    
    Returns:
        JSON com dados da análise
    
    Regras de Negócio:
        - analysis_id deve ser UUID válido
        - Retornar 404 se análise não encontrada
    """
    try:
        # TODO: Implementar AnalysisRepository.find_by_id()
        # analysis = AnalysisRepository.find_by_id(analysis_id)
        
        # Placeholder - remover quando implementar find_by_id()
        analysis = None
        
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
    """
    Busca todos os BankAnalysis de uma análise.
    
    Args:
        analysis_id: UUID da análise
    
    Returns:
        JSON com lista de BankAnalysis
    
    Regras de Negócio:
        - analysis_id deve ser UUID válido
        - Retornar 404 se análise não encontrada
        - Retornar lista vazia se não houver BankAnalysis (não erro)
    """
    try:
        # Verificar se análise existe
        # TODO: Implementar AnalysisRepository.find_by_id()
        # analysis = AnalysisRepository.find_by_id(analysis_id)
        # if not analysis:
        #     return jsonify({"error": "Análise não encontrada"}), 404
        
        # Buscar BankAnalysis
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
    """
    Cria uma nova análise.
    
    Request Body (Modo Padrão):
        {
            "name": "Análise Outubro 2024",
            "query": "OPERAÇÃO BB :: MONITORAMENTO",
            "bank_names": ["Banco do Brasil", "Itaú"],
            "start_date": "2024-10-01T00:00:00",
            "end_date": "2024-10-31T23:59:59"
        }
    
    Request Body (Modo Customizado):
        {
            "name": "Análise Customizada",
            "query": "OPERAÇÃO BB :: MONITORAMENTO",
            "custom_bank_dates": [
                {
                    "bank_name": "Banco do Brasil",
                    "start_date": "2024-10-01T00:00:00",
                    "end_date": "2024-10-31T23:59:59"
                }
            ]
        }
    
    Returns:
        JSON com mensagem de sucesso e dados da análise criada
    
    Regras de Negócio (implementadas no AnalysisService.save()):
        - name é obrigatório
        - query é obrigatório
        - Deve fornecer bank_names + start_date + end_date OU custom_bank_dates (não ambos)
        - Datas devem estar no formato ISO 8601
        - start_date < end_date
        - end_date < data atual
        - bank_names devem existir no enum BankName
        - Processamento ocorre em thread assíncrona após criação
    """
    try:
        data = request.get_json()

        name = data.get("name")
        query = data.get("query")
        bank_names = data.get("bank_names", [])
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        custom_bank_dates = data.get("custom_bank_dates", [])

        # AnalysisService.save() já valida todos os campos e regras de negócio
        analysis = analysis_service.save(
            name=name,
            query=query,
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
    """
    Lista todos os bancos disponíveis.
    
    Returns:
        JSON com lista de bancos ativos
    
    Regras de Negócio:
        - Retornar apenas bancos ativos (active = True)
        - Retornar lista vazia se não houver bancos (não erro)
    """
    try:
        # TODO: Implementar BankRepository.find_all()
        # banks = BankRepository.find_all()
        
        # Placeholder - remover quando implementar find_all()
        banks = []
        
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


# ============================================================================
# MÉTODOS A IMPLEMENTAR NOS REPOSITORIES
# ============================================================================

"""
1. AnalysisRepository.find_all()
   
   @staticmethod
   def find_all():
       '''Busca todas as análises ordenadas por data de criação (mais recente primeiro)'''
       with get_session() as session:
           return session.query(Analysis).order_by(Analysis.created_at.desc()).all()


2. AnalysisRepository.find_by_id(analysis_id: str)
   
   @staticmethod
   def find_by_id(analysis_id: str):
       '''Busca análise por ID'''
       with get_session() as session:
           return session.query(Analysis).filter(Analysis.id == analysis_id).first()


3. BankRepository.find_all()
   
   @staticmethod
   def find_all():
       '''Busca todos os bancos ativos'''
       with get_session() as session:
           return session.query(Bank).filter(Bank.active == True).all()
"""
