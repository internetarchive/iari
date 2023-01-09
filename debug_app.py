from src.models.api import create_app

app = create_app()
app.run(debug=True)
