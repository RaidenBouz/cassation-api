import logging

from src import create_app
from src.models import db

logging.basicConfig(level=logging.INFO)

app = create_app()

with app.app_context():
    db.create_all()
    logging.info("Database initialized!")
