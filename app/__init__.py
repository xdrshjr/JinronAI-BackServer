from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app(config_name="default"):
    """
    应用工厂函数，用于创建Flask应用实例
    
    Args:
        config_name (str): 配置名称，用于选择不同环境的配置
        
    Returns:
        Flask: Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    from app.config.config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    CORS(app)  # 启用CORS
    jwt = JWTManager(app)  # 初始化JWT
    
    from app.core.extensions import init_extensions
    init_extensions(app)
    
    # 注册蓝图
    from app.api.v1 import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # 注册错误处理器
    from app.core.errors import register_error_handlers
    register_error_handlers(app)
    
    @app.route('/health')
    def health_check():
        """健康检查端点"""
        return {'status': 'ok'}, 200
        
    return app 