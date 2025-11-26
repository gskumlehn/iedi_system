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
        # Remove bank analyses where IEDI is not null
        bank_analyses = [ba for ba in bank_analyses if ba.iedi_score is None]
        if not bank_analyses:
            return jsonify({"error": "Nenhuma análise de banco encontrada para esta análise"}), 404

        parent_name = "Análise de Resultado - Bancos"

        analysis_service.process_and_update_status(analysis, bank_analyses, parent_name)
        return jsonify({"message": "Processamento reiniciado com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analysis_bp.route("/api/analyses/<analysis_id>/recalculate", methods=['POST'])
def recalculate_analysis(analysis_id):
    """
    Recalcula scores IEDI de uma análise após correção de media_outlets.
    
    Fluxo:
    1. Carrega mentions do CSV
    2. Carrega media_outlets atualizados do BigQuery
    3. Recalcula mention_analysis (scores individuais)
    4. Recalcula bank_analysis (agregados)
    5. Salva CSVs atualizados
    
    Regras de Negócio:
    - Apenas análises com status COMPLETED podem ser recalculadas
    - Media_outlets devem estar atualizados no BigQuery antes de recalcular
    - Recálculo usa mesma lógica de MentionAnalysisService.create_mention_analysis()
    """
    try:
        import pandas as pd
        from pathlib import Path
        from app.repositories.media_outlet_repository import MediaOutletRepository
        from app.services.mention_analysis_service import MentionAnalysisService
        from app.infra.csv_storage import CSVStorage
        from app.enums.analysis_status import AnalysisStatus
        
        # 1. Validar análise
        analysis = AnalysisRepository.find_by_id(analysis_id)
        if not analysis:
            return jsonify({"error": "Análise não encontrada"}), 404
        
        if analysis.status != AnalysisStatus.COMPLETED:
            return jsonify({"error": f"Análise deve estar COMPLETED para recalcular. Status atual: {analysis.status.name}"}), 400
        
        # 2. Carregar mentions do CSV
        mentions_csv_path = Path(f"data/mentions_{analysis_id}.csv")
        if not mentions_csv_path.exists():
            return jsonify({"error": f"CSV de mentions não encontrado: {mentions_csv_path}"}), 404
        
        mentions_df = pd.read_csv(mentions_csv_path)
        total_mentions = len(mentions_df)
        
        # 3. Carregar media_outlets atualizados
        media_outlets = MediaOutletRepository.find_all()
        relevant_domains = {mo.domain for mo in media_outlets if not mo.is_niche}
        niche_domains = {mo.domain for mo in media_outlets if mo.is_niche}
        
        # 4. Recalcular mention_analysis
        mention_analyses = []
        
        for _, mention_row in mentions_df.iterrows():
            # Extrair dados da mention
            mention_id = mention_row['id']
            domain = mention_row['domain']
            sentiment = mention_row.get('sentiment', 'neutral')
            reach = mention_row.get('reach', 0)
            
            # Classificar veículo
            relevant_vehicle = domain in relevant_domains
            niche_vehicle = domain in niche_domains
            
            # Calcular pontos (mesma lógica de MentionAnalysisService)
            RELEVANT_OUTLET_WEIGHT = 95
            NICHE_OUTLET_WEIGHT = 54
            REACH_HIGH_WEIGHT = 100
            REACH_MEDIUM_WEIGHT = 80
            REACH_LOW_WEIGHT = 24
            TITLE_MENTIONED_WEIGHT = 40
            SUBTITLE_USED_WEIGHT = 20
            
            relevant_pts = RELEVANT_OUTLET_WEIGHT if relevant_vehicle else 0
            niche_pts = NICHE_OUTLET_WEIGHT if niche_vehicle else 0
            
            # Classificar reach
            if reach >= 1000000:
                reach_group = "HIGH"
                reach_pts = REACH_HIGH_WEIGHT
            elif reach >= 100000:
                reach_group = "MEDIUM"
                reach_pts = REACH_MEDIUM_WEIGHT
            else:
                reach_group = "LOW"
                reach_pts = REACH_LOW_WEIGHT
            
            # Título e subtítulo (assumir false se não existir)
            title_mentioned = mention_row.get('title_mentioned', False)
            subtitle_used = mention_row.get('subtitle_used', False)
            title_pts = TITLE_MENTIONED_WEIGHT if title_mentioned else 0
            subtitle_pts = SUBTITLE_USED_WEIGHT if subtitle_used else 0
            
            # Calcular IEDI
            numerator = reach_pts + relevant_pts + niche_pts + title_pts + subtitle_pts
            denominator = REACH_HIGH_WEIGHT + RELEVANT_OUTLET_WEIGHT + NICHE_OUTLET_WEIGHT + TITLE_MENTIONED_WEIGHT + SUBTITLE_USED_WEIGHT
            
            # Sentimento
            sentiment_multiplier = 1 if sentiment == 'positive' else -1 if sentiment == 'negative' else 0
            
            iedi_mean = (numerator / denominator) * 10 if denominator > 0 else 0
            iedi_score = iedi_mean * sentiment_multiplier
            
            # Criar mention_analysis
            mention_analyses.append({
                'mention_id': mention_id,
                'bank_name': mention_row.get('bank_name', ''),
                'sentiment': sentiment,
                'reach_group': reach_group,
                'niche_vehicle': niche_vehicle,
                'title_mentioned': title_mentioned,
                'subtitle_used': subtitle_used,
                'relevant_vehicle': relevant_vehicle,
                'iedi_mean': round(iedi_mean, 2),
                'iedi_score': round(iedi_score, 2)
            })
        
        # 5. Salvar mention_analysis atualizado
        mention_analysis_df = pd.DataFrame(mention_analyses)
        mention_analysis_csv_path = f"data/mention_analysis_{analysis_id}.csv"
        mention_analysis_df.to_csv(mention_analysis_csv_path, index=False)
        
        # 6. Recalcular bank_analysis (agregados)
        bank_analyses_updated = []
        bank_analyses = BankAnalysisRepository.find_by_analysis_id(analysis_id)
        
        for ba in bank_analyses:
            # Filtrar mentions deste banco
            bank_mentions = mention_analysis_df[mention_analysis_df['bank_name'] == ba.bank_name.name]
            
            if len(bank_mentions) == 0:
                continue
            
            # Calcular agregados
            total_mentions = len(bank_mentions)
            positive_mentions = bank_mentions[bank_mentions['iedi_score'] > 0]
            negative_mentions = bank_mentions[bank_mentions['iedi_score'] < 0]
            
            positive_volume = len(positive_mentions)
            negative_volume = len(negative_mentions)
            
            iedi_mean = bank_mentions['iedi_mean'].mean()
            iedi_score = bank_mentions['iedi_score'].mean()
            
            # Atualizar bank_analysis
            ba.total_mentions = total_mentions
            ba.positive_volume = float(positive_volume)
            ba.negative_volume = float(negative_volume)
            ba.iedi_mean = round(iedi_mean, 2) if not pd.isna(iedi_mean) else None
            ba.iedi_score = round(iedi_score, 2) if not pd.isna(iedi_score) else None
            
            bank_analyses_updated.append(ba)
        
        # 7. Salvar bank_analysis atualizado em CSV
        bank_analysis_data = []
        for ba in bank_analyses_updated:
            bank_analysis_data.append({
                'id': ba.id,
                'analysis_id': ba.analysis_id,
                'bank_name': ba.bank_name.name,
                'start_date': ba.start_date,
                'end_date': ba.end_date,
                'total_mentions': ba.total_mentions,
                'positive_volume': ba.positive_volume,
                'negative_volume': ba.negative_volume,
                'iedi_mean': ba.iedi_mean,
                'iedi_score': ba.iedi_score
            })
        
        bank_analysis_df = pd.DataFrame(bank_analysis_data)
        bank_analysis_csv_path = f"data/bank_analysis_{analysis_id}.csv"
        bank_analysis_df.to_csv(bank_analysis_csv_path, index=False)
        
        return jsonify({
            "message": "Recálculo concluído com sucesso",
            "details": {
                "total_mentions": total_mentions,
                "mentions_recalculated": len(mention_analyses),
                "banks_updated": len(bank_analyses_updated),
                "relevant_domains": len(relevant_domains),
                "niche_domains": len(niche_domains)
            }
        }), 200
        
    except FileNotFoundError as e:
        return jsonify({"error": f"Arquivo não encontrado: {str(e)}"}), 404
    except ValueError as e:
        return jsonify({"error": f"Erro de validação: {str(e)}"}), 400
    except Exception as e:
        import traceback
        return jsonify({
            "error": f"Erro ao recalcular: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500
