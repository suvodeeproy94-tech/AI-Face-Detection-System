"""
This file contains the face detection logic.

The route file receives a webcam frame from React. This service converts that
frame into an OpenCV image, detects faces, and returns face box details.
"""

import base64
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from config import DEFAULT_MODEL_NAME, LOCAL_HAAR_MODEL_PATH


@dataclass
class FaceBox:
    """This class stores one detected face box in a clean format."""

    x: int
    y: int
    width: int
    height: int
    confidence: float
    tracking_id: int | None = None

    def to_dict(self) -> dict:
        """Convert the face box into JSON-friendly data."""

        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
            "tracking_id": self.tracking_id,
        }


class FaceDetector:
    """Detect faces from browser webcam frames using OpenCV."""

    def __init__(self) -> None:
        """Load the Haar Cascade model once when the backend starts."""

        self.model_name = DEFAULT_MODEL_NAME
        self.classifier = self._load_haar_classifier()

    def _load_haar_classifier(self) -> cv2.CascadeClassifier:
        """Load the local model first, then use the OpenCV built-in model."""

        model_path = self._get_available_model_path()
        classifier = cv2.CascadeClassifier(str(model_path))

        if classifier.empty():
            raise RuntimeError(
                "Face detection model could not be loaded. "
                "Please check the Haar Cascade XML file."
            )

        return classifier

    def _get_available_model_path(self) -> Path:
        """Return the best available Haar Cascade model path."""

        if LOCAL_HAAR_MODEL_PATH.exists():
            return LOCAL_HAAR_MODEL_PATH

        return Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"

    def detect_from_base64_frame(self, base64_frame: str) -> dict:
        """Detect faces from a base64 webcam frame."""

        start_time = time.perf_counter()
        frame = self._decode_base64_image(base64_frame)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Equalization improves contrast and helps detection in normal light.
        gray_frame = cv2.equalizeHist(gray_frame)

        face_boxes = self._detect_faces(gray_frame)
        processing_time_ms = (time.perf_counter() - start_time) * 1000
        average_confidence = self._calculate_average_confidence(face_boxes)

        return {
            "faces": [face_box.to_dict() for face_box in face_boxes],
            "face_count": len(face_boxes),
            "average_confidence": average_confidence,
            "processing_time_ms": round(processing_time_ms, 2),
            "frame_width": int(frame.shape[1]),
            "frame_height": int(frame.shape[0]),
            "model_name": self.model_name,
        }

    def _decode_base64_image(self, base64_frame: str) -> np.ndarray:
        """Convert a browser base64 image into an OpenCV image."""

        clean_base64 = self._remove_base64_header(base64_frame)
        image_bytes = base64.b64decode(clean_base64)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if frame is None:
            raise ValueError("The received webcam frame could not be decoded.")

        return frame

    def _remove_base64_header(self, base64_frame: str) -> str:
        """Remove the browser data URL part if it is present."""

        if "," in base64_frame:
            return base64_frame.split(",", 1)[1]

        return base64_frame

    def _detect_faces(self, gray_frame: np.ndarray) -> list[FaceBox]:
        """Detect faces and return them as clear box objects."""

        try:
            rectangles, _reject_levels, level_weights = self.classifier.detectMultiScale3(
                gray_frame,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(45, 45),
                outputRejectLevels=True,
            )
        except cv2.error:
            rectangles = self.classifier.detectMultiScale(
                gray_frame,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(45, 45),
            )
            level_weights = [1.0 for _rectangle in rectangles]

        face_boxes: list[FaceBox] = []

        for rectangle, weight in zip(rectangles, level_weights):
            x_position, y_position, width, height = rectangle
            confidence = self._convert_haar_weight_to_confidence(float(weight))

            face_boxes.append(
                FaceBox(
                    x=int(x_position),
                    y=int(y_position),
                    width=int(width),
                    height=int(height),
                    confidence=confidence,
                )
            )

        return face_boxes

    def _convert_haar_weight_to_confidence(self, weight: float) -> float:
        """
        Convert Haar level weight into a simple confidence-like score.

        Haar Cascade does not return a true deep learning probability. This
        score is useful for the dashboard, but it should be explained as an
        estimated confidence during viva.
        """

        confidence = 60 + (weight * 8)
        confidence = max(50, min(confidence, 99))
        return round(confidence, 2)

    def _calculate_average_confidence(self, face_boxes: list[FaceBox]) -> float:
        """Calculate average confidence for all faces in one frame."""

        if not face_boxes:
            return 0

        total_confidence = sum(face_box.confidence for face_box in face_boxes)
        return round(total_confidence / len(face_boxes), 2)


class SimpleFaceTracker:
    """
    Track faces between frames using the center point of each box.

    This is intentionally simple. It gives a stable ID to faces without adding
    a heavy tracking library.
    """

    def __init__(self, max_distance: int = 90) -> None:
        self.max_distance = max_distance
        self.next_tracking_id = 1
        self.previous_centers: dict[int, tuple[int, int]] = {}

    def update(self, face_data: dict) -> dict:
        """Add tracking IDs to the current frame detections."""

        current_faces = face_data["faces"]
        current_centers = self._get_current_centers(current_faces)
        assigned_ids: set[int] = set()
        updated_centers: dict[int, tuple[int, int]] = {}

        for face, center in zip(current_faces, current_centers):
            tracking_id = self._find_nearest_tracking_id(center, assigned_ids)

            if tracking_id is None:
                tracking_id = self.next_tracking_id
                self.next_tracking_id += 1

            face["tracking_id"] = tracking_id
            assigned_ids.add(tracking_id)
            updated_centers[tracking_id] = center

        self.previous_centers = updated_centers
        return face_data

    def _get_current_centers(self, faces: list[dict]) -> list[tuple[int, int]]:
        """Calculate the center point of each face box."""

        centers = []

        for face in faces:
            center_x = face["x"] + face["width"] // 2
            center_y = face["y"] + face["height"] // 2
            centers.append((center_x, center_y))

        return centers

    def _find_nearest_tracking_id(
        self,
        current_center: tuple[int, int],
        assigned_ids: set[int],
    ) -> int | None:
        """Find the nearest old face ID for the current face."""

        nearest_tracking_id = None
        nearest_distance = self.max_distance

        for tracking_id, old_center in self.previous_centers.items():
            if tracking_id in assigned_ids:
                continue

            distance = self._calculate_distance(current_center, old_center)

            if distance < nearest_distance:
                nearest_tracking_id = tracking_id
                nearest_distance = distance

        return nearest_tracking_id

    def _calculate_distance(
        self,
        first_center: tuple[int, int],
        second_center: tuple[int, int],
    ) -> float:
        """Calculate normal straight-line distance between two points."""

        x_difference = first_center[0] - second_center[0]
        y_difference = first_center[1] - second_center[1]
        return float((x_difference**2 + y_difference**2) ** 0.5)
