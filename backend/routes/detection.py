"""
This file defines all face detection API routes.

React sends webcam frames to these routes. The routes call the detector service
and return simple JSON responses for the frontend dashboard.
"""

from flask import Blueprint, jsonify, request

from database import (
    clear_detection_records,
    get_detection_summary,
    get_recent_detection_records,
    save_detection_record,
)
from services.face_detector import FaceDetector, SimpleFaceTracker


detection_routes = Blueprint("detection_routes", __name__)

# These objects are created once so every frame does not reload the model.
face_detector = FaceDetector()
face_tracker = SimpleFaceTracker()


@detection_routes.get("/health")
def check_backend_health():
    """Return a simple message so the frontend can check the backend."""

    return jsonify(
        {
            "success": True,
            "message": "Face detection backend is running.",
            "model_name": face_detector.model_name,
        }
    )


@detection_routes.post("/detection/frame")
def detect_faces_from_webcam_frame():
    """Detect faces from one webcam frame sent by React."""

    request_data = request.get_json(silent=True) or {}
    frame = request_data.get("frame")

    if not frame:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Webcam frame is required.",
                }
            ),
            400,
        )

    try:
        detection_result = face_detector.detect_from_base64_frame(frame)
        tracked_result = face_tracker.update(detection_result)

        save_detection_record(
            source_type="webcam",
            face_count=tracked_result["face_count"],
            average_confidence=tracked_result["average_confidence"],
            processing_time_ms=tracked_result["processing_time_ms"],
            model_name=tracked_result["model_name"],
        )

        return jsonify(
            {
                "success": True,
                "message": "Face detection completed.",
                "data": tracked_result,
            }
        )

    except ValueError as error:
        return (
            jsonify(
                {
                    "success": False,
                    "message": str(error),
                }
            ),
            400,
        )
    except Exception:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Face detection failed. Please try again.",
                }
            ),
            500,
        )


@detection_routes.get("/detection/stats")
def get_live_detection_stats():
    """Return dashboard statistics from SQLite."""

    return jsonify(
        {
            "success": True,
            "message": "Detection statistics fetched successfully.",
            "data": get_detection_summary(),
        }
    )


@detection_routes.get("/detection/history")
def get_detection_history():
    """Return recent detection records for the dashboard."""

    limit = request.args.get("limit", default=20, type=int)
    safe_limit = min(max(limit, 1), 100)

    return jsonify(
        {
            "success": True,
            "message": "Detection history fetched successfully.",
            "data": get_recent_detection_records(limit=safe_limit),
        }
    )


@detection_routes.post("/detection/reset")
def reset_detection_history():
    """Clear saved detection records when the user resets the dashboard."""

    clear_detection_records()

    return jsonify(
        {
            "success": True,
            "message": "Detection history reset successfully.",
        }
    )
