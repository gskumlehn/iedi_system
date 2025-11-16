from flask import Blueprint, render_template, request, jsonify
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.iedi_result_repository import IEDIResultRepository
from app.repositories.analysis_mention_repository import AnalysisMentionRepository

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/")
def index():
    return render_template("analyses.html")

@analysis_bp.route("/api", methods=['GET'])
def list_analyses():
    analyses = AnalysisRepository.find_all()
    return jsonify([{
        'id': a.id,
        'period_type': a.period_type,
        'start_date': a.start_date.isoformat() if a.start_date else None,
        'end_date': a.end_date.isoformat() if a.end_date else None,
        'query_name': a.query_name,
        'created_at': a.created_at.isoformat() if a.created_at else None
    } for a in analyses])

@analysis_bp.route("/api/<string:analysis_id>", methods=['GET'])
def get_analysis(analysis_id):
    analysis = AnalysisRepository.find_by_id(analysis_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    results = IEDIResultRepository.find_by_analysis(analysis_id)
    
    return jsonify({
        'id': analysis.id,
        'period_type': analysis.period_type,
        'start_date': analysis.start_date.isoformat() if analysis.start_date else None,
        'end_date': analysis.end_date.isoformat() if analysis.end_date else None,
        'query_name': analysis.query_name,
        'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
        'results': [{
            'id': r.id,
            'bank_id': r.bank_id,
            'total_mentions': r.total_mentions,
            'final_iedi': r.final_iedi,
            'created_at': r.created_at.isoformat() if r.created_at else None
        } for r in results]
    })

@analysis_bp.route("/api/<string:analysis_id>/mentions", methods=['GET'])
def get_analysis_mentions(analysis_id):
    bank_id = request.args.get('bank_id')
    
    if bank_id:
        mentions = AnalysisMentionRepository.find_by_analysis_and_bank(analysis_id, bank_id)
    else:
        mentions = AnalysisMentionRepository.find_by_analysis(analysis_id)
    
    return jsonify([{
        'analysis_id': m.analysis_id,
        'mention_id': m.mention_id,
        'bank_id': m.bank_id,
        'iedi_score': m.iedi_score,
        'iedi_normalized': m.iedi_normalized,
        'numerator': m.numerator,
        'denominator': m.denominator,
        'title_verified': m.title_verified,
        'subtitle_verified': m.subtitle_verified,
        'relevant_outlet_verified': m.relevant_outlet_verified,
        'niche_outlet_verified': m.niche_outlet_verified,
        'created_at': m.created_at.isoformat() if m.created_at else None
    } for m in mentions])
