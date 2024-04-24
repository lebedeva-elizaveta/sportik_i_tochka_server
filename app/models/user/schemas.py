from marshmallow import Schema, fields, validate


class UserCreate(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password_hash = fields.Str(required=True, validate=validate.Length(max=255))
    name = fields.Str(required=True, validate=validate.Length(max=255))
    birthday = fields.Date(required=True, format='%Y-%m-%d')
    phone = fields.Str(required=True, validate=validate.Length(max=255))
    weight = fields.Integer(required=True)
    avatar = fields.Str()
    is_blocked = fields.Bool()


