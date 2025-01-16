from flask import Flask
from app.components.dash_app import create_dash_app

def create_app():
    app = Flask(__name__)

    # Configurar rotas principais do Flask
    @app.route('/')
    def home():
        return "<h1>Bem-vindo ao Dashboard</h1><p>Visite o <a href='/dashboard/'>Dashboard</a>.</p>"

    # Integrar Dash ao Flask
    create_dash_app(app)

    return app
