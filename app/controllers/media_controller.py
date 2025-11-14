from flask import Blueprint, render_template, request, jsonify
from app.models import Database

media_bp = Blueprint("media", __name__)
db = Database()

@media_bp.route("/relevant")
def relevant_media():
    return render_template("relevant_media.html")

@media_bp.route("/api/relevant", methods=['GET'])
def list_relevant_media():
    media = db.get_relevant_media()
    return jsonify(media)

@media_bp.route("/api/relevant", methods=['POST'])
def create_relevant_media():
    data = request.json
    media_id = db.create_relevant_media(
        name=data['name'],
        domain=data['domain'],
        active=data.get('active', True)
    )
    return jsonify({'id': media_id, 'success': True})

@media_bp.route("/api/relevant/<int:media_id>", methods=['PUT'])
def update_relevant_media(media_id):
    data = request.json
    db.update_relevant_media(
        media_id=media_id,
        name=data['name'],
        domain=data['domain'],
        active=data.get('active', True)
    )
    return jsonify({'success': True})

@media_bp.route("/api/relevant/<int:media_id>", methods=['DELETE'])
def delete_relevant_media(media_id):
    db.delete_relevant_media(media_id)
    return jsonify({'success': True})

@media_bp.route("/niche")
def niche_media():
    return render_template("niche_media.html")

@media_bp.route("/api/niche", methods=['GET'])
def list_niche_media():
    media = db.get_niche_media()
    return jsonify(media)

@media_bp.route("/api/niche", methods=['POST'])
def create_niche_media():
    data = request.json
    media_id = db.create_niche_media(
        name=data['name'],
        domain=data['domain'],
        category=data.get('category'),
        active=data.get('active', True)
    )
    return jsonify({'id': media_id, 'success': True})

@media_bp.route("/api/niche/<int:media_id>", methods=['PUT'])
def update_niche_media(media_id):
    data = request.json
    db.update_niche_media(
        media_id=media_id,
        name=data['name'],
        domain=data['domain'],
        category=data.get('category'),
        active=data.get('active', True)
    )
    return jsonify({'success': True})

@media_bp.route("/api/niche/<int:media_id>", methods=['DELETE'])
def delete_niche_media(media_id):
    db.delete_niche_media(media_id)
    return jsonify({'success': True})
