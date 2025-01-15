from unittest.mock import Mock, patch

import pytest

from src import create_app
from src.models import db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Define a test configuration
    test_config = {
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory SQLite for testing
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_SECRET_KEY": "test-jwt-secret-key",
        "TESTING": True,
        "API_TITLE": "Cour de cassation API",
        "API_VERSION": "1.0",
        "OPENAPI_VERSION": "3.0.3",
        "OPENAPI_URL_PREFIX": "/",
        "OPENAPI_SWAGGER_UI_PATH": "/",
        "OPENAPI_SWAGGER_UI_URL": "https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
    }

    # Create the app with the test configuration
    app = create_app(test_config=test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def mock_requests():
    """Fixture to mock requests.get."""
    with patch("requests.get") as mock_get:
        yield mock_get
