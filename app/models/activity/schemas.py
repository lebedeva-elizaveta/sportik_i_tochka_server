from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField

from app.models.activity.model import ActivityType


class ActivitySchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    duration = fields.Int(required=True, validate=validate.Range(min=1))
    distance_in_meters = fields.Int(required=True, validate=validate.Range(min=0))
    calories_burned = fields.Int(required=True, validate=validate.Range(min=0))
    avg_speed = fields.Float(required=True, validate=validate.Range(min=0.0))
    date = fields.Date(required=True)
    image = fields.Str(required=True)
    activity_type = EnumField(ActivityType, by_value=True, required=True)
