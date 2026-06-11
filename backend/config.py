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

# This folder stores face detection model files.
MODELS_DIR = BASE_DIR / "models"

# This is the local Haar Cascade fallback model path.
LOCAL_HAAR_MODEL_PATH = MODELS_DIR / "haarcascade_frontalface_default.xml"

# This is the stronger YuNet ONNX model path.
YUNET_MODEL_PATH = MODELS_DIR / "face_detector_model" / "face_detection_yunet_2023mar.onnx"

# This URL is documented so the model can be downloaded again if needed.
YUNET_MODEL_DOWNLOAD_URL = (
    "https://raw.githubusercontent.com/opencv/opencv_zoo/main/"
    "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
)

# Higher threshold means fewer wrong boxes, but very weak faces may be missed.
YUNET_SCORE_THRESHOLD = 0.78
YUNET_NMS_THRESHOLD = 0.3
YUNET_TOP_K = 5000

# Small weak boxes are ignored because they usually create unstable results.
MIN_FACE_WIDTH = 55
MIN_FACE_HEIGHT = 55

# This is the SQLite database file used for detection history.
DATABASE_PATH = DATA_DIR / "face_detection_records.db"

# These names are shown in API responses and dashboard statistics.
DEFAULT_MODEL_NAME = "OpenCV YuNet Face Detector"
HAAR_FALLBACK_MODEL_NAME = "OpenCV Haar Cascade Fallback"
