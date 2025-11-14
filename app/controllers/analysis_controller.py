from flask import Blueprint, render_template, request, jsonify
from app.models import Database

analysis_bp = Blueprint("analysis", __name__)
db = Database()

@analysis_bp.route("/")
def index():
    return render_template("analyses.html")

@analysis_bp.route("/api", methods=['GET'])
def list_analyses():
    analyses = db.get_analyses()
    return jsonify(analyses)

@analysis_bp.route("/api/<int:analysis_id>", methods=['GET'])
def get_analysis(analysis_id):
    analysis = db.get_analysis(analysis_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    results = db.get_results(analysis_id)
    analysis['results'] = results
    
    return jsonify(analysis)

@analysis_bp.route("/api/<int:analysis_id>/mentions", methods=['GET'])
def get_analysis_mentions(analysis_id):
    bank_id = request.args.get('bank_id', type=int)
    mentions = db.get_mentions(analysis_id, bank_id)
    return jsonify(mentions)
