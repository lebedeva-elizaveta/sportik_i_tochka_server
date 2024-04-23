from marshmallow import Schema, fields


class LoginResponseSchema(Schema):
    access_token = fields.String(required=True)
    role = fields.String(required=True)
    success = fields.Boolean(required=True)
    user_id = fields.Integer(required=True)


class UserDataSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    image = fields.String(required=True)
    phone = fields.String(required=True)
    birthday = fields.Date(required=True, format='%Y-%m-%d')
    weight = fields.Float(required=False)
