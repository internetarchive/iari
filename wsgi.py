"""This is the entry point for gunicorn"""
from src.models.api import app

if __name__ == "__main__":
    app.run()
