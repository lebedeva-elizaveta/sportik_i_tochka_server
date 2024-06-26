from marshmallow import Schema, fields, validate


class AchievementSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    image = fields.Str(required=True)
    distance = fields.Integer(required=True)
    user_id = fields.Integer(load_only=True)


class AchievementListSchema(Schema):
    achievements = fields.List(fields.Nested(AchievementSchema()))
