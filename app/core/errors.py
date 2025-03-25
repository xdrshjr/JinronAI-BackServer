from flask import jsonify

class APIError(Exception):
    """API错误基类"""
    status_code = 400
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class ValidationError(APIError):
    """验证错误"""
    status_code = 400

class AuthenticationError(APIError):
    """认证错误"""
    status_code = 401

class ForbiddenError(APIError):
    """权限错误"""
    status_code = 403

class NotFoundError(APIError):
    """资源不存在错误"""
    status_code = 404

class ServerError(APIError):
    """服务器内部错误"""
    status_code = 500

def register_error_handlers(app):
    """
    注册错误处理器到Flask应用
    
    Args:
        app: Flask应用实例
    """
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
        
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'status': 'error',
            'message': '资源未找到'
        }), 404
        
    @app.errorhandler(500)
    def handle_server_error(error):
        return jsonify({
            'status': 'error',
            'message': '服务器内部错误'
        }), 500 