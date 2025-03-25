"""
API v1版本模块
"""
from flask import Blueprint

# 创建V1版本API蓝图
api_bp = Blueprint('api_v1', __name__)

# 导入所有路由
from . import routes
from . import auth_routes
from . import agent_routes 