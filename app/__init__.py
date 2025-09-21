import os
from flask import Flask, jsonify, session
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.get("/me")
    def me():
        user = session.get("user")
        if not user:
            return jsonify({"authenticated": False}), 401
        return jsonify({"authenticated": True, "user": user})

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    return app




