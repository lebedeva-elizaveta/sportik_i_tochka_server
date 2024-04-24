from marshmallow import Schema, fields, validate


class UserCreate(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password_hash = fields.Str(required=True, validate=validate.Length(max=255))
    name = fields.Str(required=True, validate=validate.Length(max=255))
    birthday = fields.Date(required=True)
    phone = fields.Str(required=True, validate=validate.Length(max=255))
    weight = fields.Integer(required=True)
    avatar = fields.Str()
    is_blocked = fields.Bool()


class UserStatisticsSchema(Schema):
    total_distance_in_meters = fields.Float(required=True)
    total_time = fields.Float(required=True)
    total_calories = fields.Float(required=True)


class UserProfileSchema(Schema):
    name = fields.String(required=True)
    image = fields.String(required=False)
    statistics = fields.Dict(required=True)
    achievements = fields.List(fields.Dict(), required=True)
