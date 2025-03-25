"""
Flask扩展模块，集中管理所有Flask扩展
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

# 初始化SQLAlchemy，不绑定特定应用
db = SQLAlchemy()

# 初始化迁移工具，不绑定特定应用
migrate = Migrate()

# 初始化序列化工具
ma = Marshmallow()

def init_extensions(app):
    """
    初始化所有Flask扩展
    
    Args:
        app: Flask应用实例
    """
    # 初始化数据库
    db.init_app(app)
    
    # 初始化迁移
    migrate.init_app(app, db)
    
    # 初始化序列化
    ma.init_app(app) 