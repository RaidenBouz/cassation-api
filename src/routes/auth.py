from flask import jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required)
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from src.models import User, db
from src.schemas import UserSchema

auth = Blueprint(
    "auth", __name__, url_prefix="/api/v1/auth", description="Authentication operations"
)


@auth.post("/register")
@auth.arguments(
    UserSchema(only=("username", "email", "password"))
)  # Validate input using Marshmallow
@auth.response(201, UserSchema(exclude=("password",)))  # Exclude password in response
@auth.response(400, description="Invalid input (e.g., missing fields, short password)")
@auth.response(409, description="Email or username already taken")
def register(user_data):
    """
    Register a new user.
    ---
    This endpoint allows a new user to register by providing a username, email, and password.
    """
    username = user_data["username"]
    email = user_data["email"]
    password = user_data["password"]

    if User.query.filter_by(email=email).first():
        abort(409, message="Email is already taken.")

    if User.query.filter_by(username=username).first():
        abort(409, message="Username is already taken.")

    pwd_hash = generate_password_hash(password)
    user = User(username=username, email=email, password=pwd_hash)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(500, message="An error occurred while creating the user.")

    return jsonify(
        {"message": "User created", "user": {"username": username, "email": email}}
    )


@auth.post("/login")
@auth.arguments(UserSchema(only=("email", "password")))
@auth.response(200, description="Login successful")
@auth.response(400, description="Invalid input (e.g., missing fields)")
@auth.response(401, description="Invalid email or password")
def login(user_data):
    """
    Log in a user.
    ---
    This endpoint allows a user to log in by providing their email and password.
    On success, it returns access and refresh tokens.
    """
    email = user_data["email"]
    password = user_data["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        user_id = str(user.id)
        refresh = create_refresh_token(user_id)
        access = create_access_token(user_id)

        return (
            jsonify(
                {
                    "user": {
                        "refresh": refresh,
                        "access": access,
                        "username": user.username,
                        "email": user.email,
                    }
                }
            ),
            200,
        )

    abort(401, message="Invalid email or password.")


@auth.post("/refresh")
@auth.response(
    200,
    description="New access token generated",
    example={"access_token": "new_access_token"},
)
@auth.response(401, description="Invalid or expired refresh token")
@jwt_required(refresh=True)  # Only allow refresh tokens
def refresh():
    """
    Refresh an access token.
    ---
    This endpoint allows a user to refresh their access token using a valid refresh token.
    """
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_access_token}), 200
