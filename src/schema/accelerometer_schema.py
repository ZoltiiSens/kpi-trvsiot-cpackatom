from marshmallow import Schema, fields
from domain.accelerometer import Accelerometer


class AccelerometerSchema(Schema):
    x = fields.Int()
    y = fields.Int()
    z = fields.Int()
