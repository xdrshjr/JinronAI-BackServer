"""
认证相关路由
"""
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from . import api_bp
from app.core.errors import ValidationError, AuthenticationError

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    用户登录
    
    Returns:
        JSON: 包含token的响应
    """
    if not request.is_json:
        raise ValidationError('缺少JSON数据')
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not username or not password:
        raise ValidationError('缺少用户名或密码')
    
    # TODO: 实现实际的用户验证逻辑
    # 这里仅用于演示，实际项目中需要从数据库验证
    if username != 'admin' or password != 'password':
        raise AuthenticationError('无效的用户名或密码')
    
    # 创建访问令牌和刷新令牌
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    
    return jsonify({
        'status': 'success',
        'message': '登录成功',
        'access_token': access_token,
        'refresh_token': refresh_token
    })

@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    刷新访问令牌
    
    Returns:
        JSON: 包含新token的响应
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    
    return jsonify({
        'status': 'success',
        'message': '令牌刷新成功',
        'access_token': access_token
    })

@api_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def profile():
    """
    获取当前用户信息
    
    Returns:
        JSON: 用户信息
    """
    current_user = get_jwt_identity()
    
    # TODO: 从数据库获取完整的用户信息
    # 这里仅返回用户名
    
    return jsonify({
        'status': 'success',
        'user': {
            'username': current_user
        }
    }) 