"""
示例Agent实现
"""
from .base_agent import BaseAgent

class DemoAgent(BaseAgent):
    """
    示例Agent，提供基本的回声功能
    """
    
    def initialize(self):
        """
        初始化Agent
        """
        self.name = self.config.get('name', 'Demo Agent')
        print(f"{self.name} 已初始化")
        
    def process(self, input_data, **kwargs):
        """
        处理输入数据，简单返回输入
        
        Args:
            input_data: 输入数据
            **kwargs: 额外参数
            
        Returns:
            dict: 处理结果
        """
        # 仅作示例，实际Agent应实现更复杂的处理逻辑
        return {
            'agent_name': self.name,
            'input': input_data,
            'output': f"Echo: {input_data}",
            'kwargs': kwargs
        }
        
    def cleanup(self):
        """
        清理资源
        """
        print(f"{self.name} 资源已清理") 