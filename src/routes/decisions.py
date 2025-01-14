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

@decisions.get("/search")
@decisions.response(200, DecisionSchema(many=True))
@jwt_required()
def search_decisions():
    q = request.args.get('q', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    if not q:
        return jsonify({"data": []})
    
    search_terms = q.split()
    
    # Step 1: Query for relevant decisions
    query = Decision.query.filter(
        Decision.title.ilike(f"%{q}%") | 
        Decision.content.ilike(f"%{q}%")
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
        
        data.append({
            'id': decision.id,
            'title': decision.title,
            'score': score
        })
    
    data_sorted = sorted(data, key=lambda x: x['score'], reverse=True)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = data_sorted[start:end]
    
    meta = {
        "page": page,
        "pages": (len(data_sorted) + per_page - 1) // per_page,
        "total_count": len(data_sorted),
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if end < len(data_sorted) else None,
        'has_next': end < len(data_sorted),
        "has_prev": start > 0
    }
    
    return jsonify({"data": paginated_data, "meta": meta})
