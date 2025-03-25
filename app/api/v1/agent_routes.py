"""
Agent相关路由
"""
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from . import api_bp
from app.agents import get_agent
from app.core.errors import ValidationError

@api_bp.route('/agents', methods=['GET'])
@jwt_required()
def list_agent_types():
    """
    列出所有可用的Agent类型
    
    Returns:
        JSON: 包含Agent类型列表的响应
    """
    from app.agents.agent_factory import AGENT_TYPES
    
    return jsonify({
        'status': 'success',
        'agent_types': list(AGENT_TYPES.keys())
    })

@api_bp.route('/agents/process', methods=['POST'])
@jwt_required()
def process_with_agent():
    """
    使用指定Agent处理请求
    
    Returns:
        JSON: 处理结果
    """
    if not request.is_json:
        raise ValidationError('请求必须是JSON格式')
        
    # 获取请求数据
    data = request.json
    agent_type = data.get('agent_type')
    agent_config = data.get('config', {})
    input_data = data.get('input')
    
    # 验证必要字段
    if not agent_type:
        raise ValidationError('缺少agent_type字段')
    if input_data is None:
        raise ValidationError('缺少input字段')
        
    # 获取Agent实例
    agent = get_agent(agent_type, agent_config)
    
    # 处理输入
    result = agent.process(input_data)
    
    return jsonify({
        'status': 'success',
        'agent_type': agent_type,
        'result': result
    }) 