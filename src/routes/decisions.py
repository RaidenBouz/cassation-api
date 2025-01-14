from flask import request
from flask_smorest import Blueprint, abort
from flask.json import jsonify
from flask_jwt_extended import jwt_required
from src.schemas import DecisionSchema
from src.models import Decision

decisions = Blueprint("decisions", __name__, url_prefix="/api/v1/decisions", description="Operations on decisions")


@decisions.get("/")
@decisions.response(200, DecisionSchema(many=True))
@jwt_required()
def get_decisions():
    """
    Get a paginated list of decisions.
    ---
    This endpoint returns a paginated list of decisions, optionally filtered by formation.
    """

    formation = request.args.get("formation")
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    query = Decision.query.with_entities(Decision.id, Decision.title, Decision.formation)
    if formation:
        query = query.filter_by(formation=formation)

    decisions_paginated = query.paginate(page=page, per_page=per_page)

    decision_schema = DecisionSchema(many=True)
    data = decision_schema.dump(decisions_paginated.items)

    # Build the pagination metadata
    meta = {
        "page": decisions_paginated.page,
        "pages": decisions_paginated.pages,
        "total_count": decisions_paginated.total,
        "prev_page": decisions_paginated.prev_num,
        "next_page": decisions_paginated.next_num,
        "has_next": decisions_paginated.has_next,
        "has_prev": decisions_paginated.has_prev,
    }

    return jsonify({"data": data, "meta": meta})

@decisions.get("/<string:id>")
@decisions.response(200, DecisionSchema())
@decisions.response(404, description="Decision not found")
@jwt_required()
def get_decision(id):
    """
    Get a single decision's content by ID.
    ---
    This endpoint returns a decision content by its ID.
    """
    decision = Decision.query.filter_by(id=id).first()

    if not decision:
        abort(404, message="Decision not found")

    # Serialize the decision using DecisionSchema
    decision_schema = DecisionSchema(only=("content",))
    return decision_schema.dump(decision)