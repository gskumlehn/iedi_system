from flask import Blueprint, jsonify, render_template, request
from app.repositories.media_outlet_repository import MediaOutletRepository

media_bp = Blueprint('media', __name__, url_prefix='/media')

@media_bp.route("/")
def index():
    return render_template('media.html')

@media_bp.route("/api", methods=['GET'])
def list_outlets():
    is_niche_param = request.args.get('niche')
    is_niche = None
    
    if is_niche_param is not None:
        is_niche = is_niche_param.lower() == 'true'
    
    outlets = MediaOutletRepository.list_all(is_niche=is_niche)
    return jsonify(outlets)

@media_bp.route("/api/<int:outlet_id>", methods=['GET'])
def get_outlet(outlet_id):
    outlet = MediaOutletRepository.get_by_id(outlet_id)
    if not outlet:
        return jsonify({'error': 'Media outlet not found'}), 404
    return jsonify(outlet)

@media_bp.route("/api", methods=['POST'])
def create_outlet():
    data = request.json
    
    if not data.get('name') or not data.get('domain'):
        return jsonify({'error': 'Name and domain are required'}), 400
    
    outlet = MediaOutletRepository.create(
        name=data['name'],
        domain=data['domain'],
        category=data.get('category'),
        monthly_visitors=data.get('monthly_visitors'),
        is_niche=data.get('is_niche', False)
    )
    
    return jsonify(outlet), 201

@media_bp.route("/api/<int:outlet_id>", methods=['PUT'])
def update_outlet(outlet_id):
    data = request.json
    
    outlet = MediaOutletRepository.update(
        outlet_id=outlet_id,
        name=data.get('name'),
        domain=data.get('domain'),
        category=data.get('category'),
        monthly_visitors=data.get('monthly_visitors'),
        is_niche=data.get('is_niche'),
        active=data.get('active')
    )
    
    if not outlet:
        return jsonify({'error': 'Media outlet not found'}), 404
    
    return jsonify(outlet)

@media_bp.route("/api/<int:outlet_id>", methods=['DELETE'])
def delete_outlet(outlet_id):
    success = MediaOutletRepository.delete(outlet_id)
    
    if not success:
        return jsonify({'error': 'Media outlet not found'}), 404
    
    return jsonify({'message': 'Media outlet deleted successfully'})
