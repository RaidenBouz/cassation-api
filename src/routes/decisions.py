from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from src.models import Decision
from src.schemas import (DecisionSchema, FilteredPaginationSchema,
                         SearchQuerySchema)

decisions = Blueprint(
    "decisions",
    __name__,
    url_prefix="/api/v1/decisions",
    description="Operations on decisions",
)


@decisions.get("/")
@decisions.arguments(FilteredPaginationSchema, location="query")
@decisions.response(
    200,
    DecisionSchema(exclude=("content",)),
    description="A paginated list of decisions",
)
@decisions.response(401, description="Unauthorized - JWT token is missing or invalid")
@jwt_required()
def get_decisions(args):
    """
    Get a paginated list of decisions.
    ---
    This endpoint returns a paginated list of decisions, optionally filtered by formation.
    Query Parameters:
      - formation: Filter decisions by formation (optional).
      - page: Page number for pagination (default: 1).
      - per_page: Number of decisions per page (default: 5).
    """
    formation = args.get("formation")
    page = int(args.get("page", 1))
    per_page = int(request.args.get("per_page", 5))

    query = Decision.query.with_entities(
        Decision.id, Decision.title, Decision.formation
    )
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
@decisions.response(200, example={"content": "string"})
@jwt_required()
def get_decision(id):
    """
    Restore the original response structure.
    """
    decision = Decision.query.filter_by(id=id).first()

    if not decision:
        return {"message": "Decision not found", "id": id}, 404

    # Serialize the decision using DecisionSchema
    decision_schema = DecisionSchema(only=("content",))
    serialized_decision = decision_schema.dump(decision)

    return serialized_decision, 200


@decisions.get("/search")
@decisions.arguments(SearchQuerySchema, location="query")
@decisions.response(
    200,
    example={
        "id": "string",
        "title": "string",
        "score": "integer",
        "content": "string",
    },
    description="A list of decisions matching the search query",
)
@decisions.response(401, description="Unauthorized - JWT token is missing or invalid")
@jwt_required()
def search_decisions(args):
    """
    Search decisions by title or content.
    ---
    This endpoint allows searching decisions by a query string. It searches both the title and content fields.
    Query Parameters:
      - q: The search query string.
      - page: Page number for pagination (default: 1).
      - per_page: Number of decisions per page (default: 5).
    """
    q = args.get("q", "").strip().lower()
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 5))

    if not q:
        return jsonify({"data": []})

    search_terms = q.split()

    query = Decision.query.filter(
        Decision.title.ilike(f"%{q}%") | Decision.content.ilike(f"%{q}%")
    )

    decisions = query.all()

    # Calculate relevance scores
    data = []
    for decision in decisions:
        score = 0
        title_tokens = decision.title.lower().split()
        content_tokens = decision.content.lower().split()

        for term in search_terms:
            score += title_tokens.count(term) * 2  # Weighted score for title matches
            score += content_tokens.count(term)  # Lesser weight for content matches

        data.append(
            {
                "id": decision.id,
                "title": decision.title,
                "content": decision.content,
                "score": score,
            }
        )

    data_sorted = sorted(data, key=lambda x: x["score"], reverse=True)
    # manual pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = data_sorted[start:end]

    meta = {
        "page": page,
        "pages": (len(data_sorted) + per_page - 1) // per_page,
        "total_count": len(data_sorted),
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if end < len(data_sorted) else None,
        "has_next": end < len(data_sorted),
        "has_prev": start > 0,
    }

    return jsonify({"data": paginated_data, "meta": meta})
