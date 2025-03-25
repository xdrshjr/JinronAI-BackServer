"""
基础Agent类
"""
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    基础Agent抽象类，所有Agent必须继承此类
    """
    
    def __init__(self, config=None):
        """
        初始化Agent
        
        Args:
            config: Agent配置
        """
        self.config = config or {}
        self.initialize()
        
    def initialize(self):
        """
        初始化Agent，可被子类重写
        """
        pass
        
    @abstractmethod
    def process(self, input_data, **kwargs):
        """
        处理输入数据
        
        Args:
            input_data: 输入数据
            **kwargs: 额外参数
            
        Returns:
            处理结果
        """
        pass
        
    def cleanup(self):
        """
        清理资源，可被子类重写
        """
        pass
        
    def __del__(self):
        """
        析构函数，确保资源被清理
        """
        self.cleanup() 