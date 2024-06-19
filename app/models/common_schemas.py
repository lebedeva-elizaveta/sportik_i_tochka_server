from marshmallow import Schema, fields, validate


class LoginRequestSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.Str(required=True, validate=validate.Length(max=255))


class LoginResponseSchema(Schema):
    access_token = fields.String(required=True)
    role = fields.String(required=True)
    success = fields.Boolean(required=True)
    entity_id = fields.Integer(required=True)


class EntityGetSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    image = fields.String(required=True)
    phone = fields.String(required=True)
    birthday = fields.Date(required=True, format='%Y-%m-%d')
    weight = fields.Float(required=False)


class EntityUpdateSchema(Schema):
    name = fields.String(required=False)
    image = fields.String(required=False)
    phone = fields.String(required=False)
    birthday = fields.Date(required=False, format='%Y-%m-%d')
    weight = fields.Float(required=False, allow_none=True)
