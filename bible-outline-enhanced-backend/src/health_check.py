"""
Health check endpoint for Render deployment
"""

from flask import Blueprint, jsonify
import os
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'bible-outline-backend',
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'timestamp': str(datetime.utcnow())
    }), 200

