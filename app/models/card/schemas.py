from datetime import datetime

from marshmallow import Schema, fields, validate, pre_load


class CardData(Schema):
    card_name = fields.Str(required=True, validate=[validate.Length(min=1, max=100)])
    card_number = fields.Str(
        required=True,
        validate=[validate.Regexp(r"^\d{16}$", error="Card number must contain 16 digits")]
    )
    month = fields.Int(
        required=True,
        validate=[
            validate.Range(min=1, max=12, error="Month must be between 1 and 12"),
            lambda x: x >= datetime.utcnow().month if x == datetime.utcnow().year else True
        ]
    )

    @pre_load
    def adjust_year(self, data, **kwargs):
        if 'year' in data:
            year_str = str(data['year'])
            if len(year_str) == 2:
                current_year = datetime.utcnow().year
                current_century = (current_year // 100) * 100
                year = int(year_str)
                if year < current_year % 100:
                    data['year'] = current_century + year
                else:
                    data['year'] = current_century + year
            else:
                data['year'] = int(data['year'])
        return data

    year = fields.Int(
        required=True,
        validate=[validate.Range(min=datetime.utcnow().year, error="Year must be current or future")]
    )
    cvv = fields.Int(
        required=True,
        validate=[
            validate.Range(min=100, max=999, error="CVV must be a 3-digit integer")
        ]
    )


class EncryptedCardSchema(Schema):
    card_name = fields.Str(required=True)
    card_number = fields.Str(required=True)
    month = fields.Str(required=True)
    year = fields.Str(required=True)
    cvv = fields.Str(required=True)
