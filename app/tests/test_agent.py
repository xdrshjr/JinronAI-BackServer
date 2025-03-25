"""
Agent测试
"""
import unittest
from app.agents import get_agent
from app.core.errors import ValidationError

class AgentTestCase(unittest.TestCase):
    """Agent测试类"""
    
    def test_demo_agent(self):
        """测试DemoAgent"""
        # 创建Demo Agent实例
        agent = get_agent('demo', {'name': 'Test Agent'})
        
        # 测试处理方法
        result = agent.process('Hello, Agent!')
        self.assertEqual(result['agent_name'], 'Test Agent')
        self.assertEqual(result['input'], 'Hello, Agent!')
        self.assertEqual(result['output'], 'Echo: Hello, Agent!')
        
    def test_invalid_agent_type(self):
        """测试无效的Agent类型"""
        with self.assertRaises(ValidationError):
            get_agent('invalid_type')
            
if __name__ == '__main__':
    unittest.main() 