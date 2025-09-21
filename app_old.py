from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from db import init_db
from auth import auth_bp

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Initialize CORS
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
    
    # Initialize database
    init_db(app)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app