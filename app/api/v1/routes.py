"""
API路由模块
"""
from flask import jsonify, request
from . import api_bp

@api_bp.route('/', methods=['GET'])
def index():
    """API根路径"""
    return jsonify({
        'message': 'Welcome to the API',
        'version': 'v1',
        'status': 'ok'
    })

@api_bp.route('/ping', methods=['GET'])
def ping():
    """API健康检查"""
    return jsonify({
        'message': 'pong',
        'status': 'ok'
    }) 