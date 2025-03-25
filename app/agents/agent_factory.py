"""
Agent工厂模块
"""
from app.core.errors import ValidationError
from .demo_agent import DemoAgent

# Agent类型映射
AGENT_TYPES = {
    'demo': DemoAgent,
    # 在这里添加更多Agent类型
}

def get_agent(agent_type, config=None):
    """
    获取指定类型的Agent实例
    
    Args:
        agent_type (str): Agent类型名称
        config (dict, optional): Agent配置
        
    Returns:
        BaseAgent: Agent实例
        
    Raises:
        ValidationError: 无效的Agent类型
    """
    if agent_type not in AGENT_TYPES:
        raise ValidationError(f"无效的Agent类型: {agent_type}，支持的类型: {', '.join(AGENT_TYPES.keys())}")
        
    # 获取Agent类
    agent_class = AGENT_TYPES[agent_type]
    
    # 创建并返回Agent实例
    return agent_class(config) 