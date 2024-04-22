from marshmallow import Schema, fields


class LoginResponseSchema(Schema):
    access_token = fields.String(required=True)
    role = fields.String(required=True)
    success = fields.Boolean(required=True)
    user_id = fields.Integer(required=True)
