"""
This is the main Flask backend file.

It starts the API server, prepares the database, and connects the face
detection routes with the frontend.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from config import DATA_DIR, MODELS_DIR
from database import setup_database
from routes.detection import detection_routes


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # CORS allows local React dev servers to call this Flask backend.
    # Vite may use 5173, 5174, or another port if the first port is busy.
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    r"http://127\.0\.0\.1:\d+",
                    r"http://localhost:\d+",
                ]
            }
        },
    )

    prepare_backend_folders()
    setup_database()

    app.register_blueprint(detection_routes, url_prefix="/api")

    @app.get("/")
    def home():
        """Return a simple backend status message."""

        return jsonify(
            {
                "success": True,
                "message": "AI-Based Real-Time Face Detection API is running.",
                "api_health_url": "/api/health",
            }
        )

    return app


def prepare_backend_folders() -> None:
    """Create required backend folders if they do not exist."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
