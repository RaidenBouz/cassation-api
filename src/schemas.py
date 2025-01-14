from marshmallow import Schema, fields, validate

class DecisionSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    formation = fields.String(required=True, validate=validate.Length(min=1, max=255))
    content = fields.String(required=True)

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    email = fields.String(required=True, validate=validate.Email())
    password = fields.String(required=True, validate=validate.Length(min=8), load_only=True)  # Prevents password from being serialized
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)