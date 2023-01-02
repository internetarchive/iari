"""This is the entry point for gunicorn"""
from src.models.api import create_app

app = create_app()
