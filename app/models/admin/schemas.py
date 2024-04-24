from marshmallow import Schema, fields, validate


class AdminCreate(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password_hash = fields.Str(required=True, validate=validate.Length(max=255))
    name = fields.Str(required=True, validate=validate.Length(max=255))
    birthday = fields.Date(required=True)
    phone = fields.Str(required=True, validate=validate.Length(max=255))
    avatar = fields.Str()


class AdminGrantPremiumSchema(Schema):
    user_id = fields.Int(required=True)


class AdminActionModifySchema(Schema):
    user_id = fields.Int(required=True)
    action = fields.Str(required=True, validate=lambda x: x.upper() in ["BLOCK", "UNBLOCK", "REVOKE_PREMIUM"])


class AdminProfileSchema(Schema):
    name = fields.String(required=True)
    image = fields.String(required=False)
