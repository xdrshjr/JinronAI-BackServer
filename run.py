"""
应用启动脚本
"""
import os
from app import create_app
from app.core.extensions import db
from app.models import User

# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG') or 'development')

@app.shell_context_processor
def make_shell_context():
    """为Flask shell添加上下文"""
    return dict(db=db, User=User)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 