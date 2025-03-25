"""
用户数据模式
"""
from marshmallow import fields, validate
from app.core.extensions import ma
from app.models.user_model import User

class UserSchema(ma.SQLAlchemySchema):
    """用户数据模式"""
    class Meta:
        model = User
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(
        required=True,
        validate=validate.Length(min=3, max=64)
    )
    email = ma.auto_field(
        required=True,
        validate=validate.Email()
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        load_only=True
    )
    is_active = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)
    
    # 用于创建用户的模式
    user_create = ma.auto_field(exclude=("id", "created_at", "updated_at")) 