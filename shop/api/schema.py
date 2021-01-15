from marshmallow import Schema, fields
from marshmallow.validate import Length


class AddCategorySchema(Schema):
    title = fields.String()
    parent = fields.String()


class AddProductSchema(Schema):
    title = fields.String(validate=Length(max=256))
    description = fields.String(validate=Length(max=500))
    discount = fields.Integer(validate=Length(min=0, max=100))
    price = fields.Float()
    category = fields.String()