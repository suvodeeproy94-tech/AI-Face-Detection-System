"""
This file stores simple backend settings.

The Flask app, database helper, and face detector use these values so that
important paths stay in one easy place.
"""

from pathlib import Path


# This is the main backend folder.
BASE_DIR = Path(__file__).resolve().parent

# This folder stores the local SQLite database.
DATA_DIR = BASE_DIR / "data"

# This folder can store model files if we add advanced models later.
MODELS_DIR = BASE_DIR / "models"

# This is the local Haar Cascade file path.
LOCAL_HAAR_MODEL_PATH = MODELS_DIR / "haarcascade_frontalface_default.xml"

# This is the SQLite database file used for detection history.
DATABASE_PATH = DATA_DIR / "face_detection_records.db"

# Frontend runs on this URL during local development.
FRONTEND_LOCAL_URL = "http://localhost:5173"

# This model name is shown in API responses and dashboard statistics.
DEFAULT_MODEL_NAME = "OpenCV Haar Cascade"
