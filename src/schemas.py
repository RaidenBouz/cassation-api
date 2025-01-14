from marshmallow import Schema, fields, validate


class DecisionSchema(Schema):
    id = fields.String(dump_only=True)
    title = fields.String(required=True)
    formation = fields.String(required=True, validate=validate.Length(min=1, max=255))
    content = fields.String(required=True)


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    email = fields.String(required=True, validate=validate.Email())
    password = fields.String(
        required=True, validate=validate.Length(min=8), load_only=True
    )  # Prevents password from being serialized
    created_at = fields.DateTime(dump_only=True)


class PaginationSchema(Schema):
    page = fields.Integer(
        required=False,
        missing=1,
        description="Page number for pagination (default: 1).",
    )
    per_page = fields.Integer(
        required=False, missing=5, description="Number of items per page (default: 5)."
    )


class FilteredPaginationSchema(PaginationSchema):
    formation = fields.String(
        required=False, description="Filter decisions by formation (optional)."
    )


class SearchQuerySchema(PaginationSchema):
    q = fields.String(required=False, description="The search query string.")
