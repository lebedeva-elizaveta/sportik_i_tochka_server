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


class UserAverageStatisticsSchema(Schema):
    avg_speed = fields.Float(required=True)
    average_distance_in_meters = fields.Float(required=True)
    average_time = fields.Float(required=True)
    average_calories = fields.Float(required=True)


class UserDataForRatingSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    image = fields.String(required=False)
    role = fields.String(required=True)
    rating = fields.Integer(required=True)
    total_activities_count = fields.Integer(required=True)
    total_distance_in_meters = fields.Float(required=True)
    total_time = fields.Float(required=True)
    total_calories = fields.Float(required=True)
    avg_speed = fields.Float(required=True)
    average_distance_in_meters = fields.Float(required=True)
    average_time = fields.Float(required=True)
    average_calories = fields.Float(required=True)
    achievements = fields.List(fields.Dict, required=True)