"""
用户服务
"""
from app.models.user_model import User
from app.core.extensions import db
from app.core.errors import ValidationError, NotFoundError, ServerError

class UserService:
    """用户服务类"""
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        通过ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User: 用户对象
            
        Raises:
            NotFoundError: 用户不存在
        """
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError(f"用户ID {user_id} 不存在")
        return user
    
    @staticmethod
    def get_user_by_username(username):
        """
        通过用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email):
        """
        通过邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def create_user(username, email, password):
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            ValidationError: 用户名或邮箱已存在
            ServerError: 创建用户失败
        """
        # 检查用户名是否已存在
        if UserService.get_user_by_username(username):
            raise ValidationError("用户名已存在")
            
        # 检查邮箱是否已存在
        if UserService.get_user_by_email(email):
            raise ValidationError("邮箱已存在")
            
        try:
            # 创建新用户
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise ServerError(f"创建用户失败: {str(e)}")
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段
            
        Returns:
            User: 更新后的用户对象
            
        Raises:
            NotFoundError: 用户不存在
            ValidationError: 无效的更新字段
            ServerError: 更新用户失败
        """
        user = UserService.get_user_by_id(user_id)
        
        try:
            # 更新允许的字段
            for key, value in kwargs.items():
                if key == 'password':
                    user.set_password(value)
                elif key in ['username', 'email', 'is_active']:
                    setattr(user, key, value)
                else:
                    # 忽略不允许更新的字段
                    pass
                    
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise ServerError(f"更新用户失败: {str(e)}")
    
    @staticmethod
    def delete_user(user_id):
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 删除成功返回True
            
        Raises:
            NotFoundError: 用户不存在
            ServerError: 删除用户失败
        """
        user = UserService.get_user_by_id(user_id)
        
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ServerError(f"删除用户失败: {str(e)}")
    
    @staticmethod
    def authenticate(username, password):
        """
        用户认证
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            User: 认证成功返回用户对象，否则返回None
        """
        user = UserService.get_user_by_username(username)
        if user and user.check_password(password) and user.is_active:
            return user
        return None 