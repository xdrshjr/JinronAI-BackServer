"""
基本功能测试
"""
import unittest
from app import create_app
from app.core.extensions import db

class BasicTestCase(unittest.TestCase):
    """基本功能测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
    def tearDown(self):
        """测试后置清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_app_exists(self):
        """测试应用是否存在"""
        self.assertIsNotNone(self.app)
        
    def test_app_is_testing(self):
        """测试是否处于测试模式"""
        self.assertTrue(self.app.config['TESTING'])
        
    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')
        
    def test_api_index(self):
        """测试API根路径"""
        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')
        
if __name__ == '__main__':
    unittest.main() 