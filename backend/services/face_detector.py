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

from config import (
    DEFAULT_MODEL_NAME,
    HAAR_FALLBACK_MODEL_NAME,
    LOCAL_HAAR_MODEL_PATH,
    MIN_FACE_HEIGHT,
    MIN_FACE_WIDTH,
    YUNET_MODEL_PATH,
    YUNET_NMS_THRESHOLD,
    YUNET_SCORE_THRESHOLD,
    YUNET_TOP_K,
)


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
        """Load YuNet first and keep Haar Cascade as a safe fallback."""

        self.model_name = HAAR_FALLBACK_MODEL_NAME
        self.haar_classifier = self._load_haar_classifier()
        self.yunet_detector = self._load_yunet_detector()

        if self.yunet_detector is not None:
            self.model_name = DEFAULT_MODEL_NAME

    def _load_yunet_detector(self):
        """Load the stronger YuNet model when the ONNX file is available."""

        if not hasattr(cv2, "FaceDetectorYN"):
            return None

        if not YUNET_MODEL_PATH.exists():
            return None

        return cv2.FaceDetectorYN.create(
            str(YUNET_MODEL_PATH),
            "",
            (640, 480),
            YUNET_SCORE_THRESHOLD,
            YUNET_NMS_THRESHOLD,
            YUNET_TOP_K,
        )

    def _load_haar_classifier(self) -> cv2.CascadeClassifier:
        """Load the local Haar model first, then use the OpenCV built-in model."""

        model_path = self._get_available_haar_model_path()
        classifier = cv2.CascadeClassifier(str(model_path))

        if classifier.empty():
            raise RuntimeError(
                "Fallback face detection model could not be loaded. "
                "Please check the Haar Cascade XML file."
            )

        return classifier

    def _get_available_haar_model_path(self) -> Path:
        """Return the best available Haar Cascade model path."""

        if LOCAL_HAAR_MODEL_PATH.exists():
            return LOCAL_HAAR_MODEL_PATH

        return Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"

    def get_status(self) -> dict:
        """Return model status for health checks and viva explanation."""

        return {
            "active_model": self.model_name,
            "yunet_available": self.yunet_detector is not None,
            "yunet_model_path": str(YUNET_MODEL_PATH),
            "fallback_model": HAAR_FALLBACK_MODEL_NAME,
            "target_accuracy_note": (
                "95% accuracy must be measured on a labeled test dataset."
            ),
        }

    def detect_from_base64_frame(self, base64_frame: str) -> dict:
        """Detect faces from a base64 webcam frame."""

        frame = self._decode_base64_image(base64_frame)
        return self.detect_from_image_array(frame)

    def detect_from_image_file(self, image_path: str | Path) -> dict:
        """Detect faces from an image file. This is used by accuracy scripts."""

        frame = cv2.imread(str(image_path))

        if frame is None:
            raise ValueError(f"Image could not be read: {image_path}")

        return self.detect_from_image_array(frame)

    def detect_from_image_array(self, frame: np.ndarray) -> dict:
        """Detect faces from an OpenCV image array."""

        start_time = time.perf_counter()
        prepared_frame = self._prepare_frame_for_detection(frame)
        face_boxes = self._detect_faces(prepared_frame)
        processing_time_ms = (time.perf_counter() - start_time) * 1000
        average_confidence = self._calculate_average_confidence(face_boxes)
        quality_result = self._get_frame_quality(frame, face_boxes, average_confidence)

        return {
            "faces": [face_box.to_dict() for face_box in face_boxes],
            "face_count": len(face_boxes),
            "average_confidence": average_confidence,
            "processing_time_ms": round(processing_time_ms, 2),
            "frame_width": int(frame.shape[1]),
            "frame_height": int(frame.shape[0]),
            "model_name": self.model_name,
            "yunet_available": self.yunet_detector is not None,
            "quality_status": quality_result["status"],
            "quality_message": quality_result["message"],
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

    def _prepare_frame_for_detection(self, frame: np.ndarray) -> np.ndarray:
        """
        Improve very dark or very bright webcam frames before detection.

        This small preprocessing step helps the detector in normal room light.
        It keeps the code simple and easy to explain.
        """

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        average_brightness = float(np.mean(gray_frame))

        if average_brightness < 75:
            return cv2.convertScaleAbs(frame, alpha=1.25, beta=35)

        if average_brightness > 190:
            return cv2.convertScaleAbs(frame, alpha=0.9, beta=-12)

        return frame

    def _detect_faces(self, frame: np.ndarray) -> list[FaceBox]:
        """
        Use YuNet when available.

        If YuNet is active and it finds no face, we return no face instead of
        falling back to Haar. This reduces false detections and makes mistakes
        less common.
        """

        if self.yunet_detector is not None:
            self.model_name = DEFAULT_MODEL_NAME
            return self._detect_faces_with_yunet(frame)

        self.model_name = HAAR_FALLBACK_MODEL_NAME
        return self._detect_faces_with_haar(frame)

    def _detect_faces_with_yunet(self, frame: np.ndarray) -> list[FaceBox]:
        """Detect faces using the stronger OpenCV YuNet model."""

        frame_height, frame_width = frame.shape[:2]
        self.yunet_detector.setInputSize((frame_width, frame_height))

        _status, detections = self.yunet_detector.detect(frame)

        if detections is None:
            return []

        face_boxes: list[FaceBox] = []

        for detection in detections:
            confidence = round(float(detection[-1]) * 100, 2)

            if confidence < YUNET_SCORE_THRESHOLD * 100:
                continue

            face_box = self._create_clipped_face_box(
                detection=detection,
                frame_width=frame_width,
                frame_height=frame_height,
                confidence=confidence,
            )

            if face_box is not None:
                face_boxes.append(face_box)

        return face_boxes

    def _create_clipped_face_box(
        self,
        detection: np.ndarray,
        frame_width: int,
        frame_height: int,
        confidence: float,
    ) -> FaceBox | None:
        """Create one clean face box and keep it inside the camera frame."""

        x_position = max(0, int(round(float(detection[0]))))
        y_position = max(0, int(round(float(detection[1]))))
        right_position = min(frame_width, x_position + int(round(float(detection[2]))))
        bottom_position = min(frame_height, y_position + int(round(float(detection[3]))))

        width = right_position - x_position
        height = bottom_position - y_position

        if width < MIN_FACE_WIDTH or height < MIN_FACE_HEIGHT:
            return None

        return FaceBox(
            x=x_position,
            y=y_position,
            width=width,
            height=height,
            confidence=confidence,
        )

    def _detect_faces_with_haar(self, frame: np.ndarray) -> list[FaceBox]:
        """Detect faces using Haar Cascade fallback."""

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Equalization improves contrast for the older Haar fallback model.
        gray_frame = cv2.equalizeHist(gray_frame)

        try:
            rectangles, _reject_levels, level_weights = (
                self.haar_classifier.detectMultiScale3(
                    gray_frame,
                    scaleFactor=1.08,
                    minNeighbors=7,
                    minSize=(MIN_FACE_WIDTH, MIN_FACE_HEIGHT),
                    outputRejectLevels=True,
                )
            )
        except cv2.error:
            rectangles = self.haar_classifier.detectMultiScale(
                gray_frame,
                scaleFactor=1.08,
                minNeighbors=7,
                minSize=(MIN_FACE_WIDTH, MIN_FACE_HEIGHT),
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

        Haar Cascade does not return a true deep learning probability. YuNet
        returns a real score, but this fallback keeps the response format same.
        """

        confidence = 56 + (weight * 7)
        confidence = max(50, min(confidence, 88))
        return round(confidence, 2)

    def _calculate_average_confidence(self, face_boxes: list[FaceBox]) -> float:
        """Calculate average confidence for all faces in one frame."""

        if not face_boxes:
            return 0

        total_confidence = sum(face_box.confidence for face_box in face_boxes)
        return round(total_confidence / len(face_boxes), 2)

    def _get_frame_quality(
        self,
        frame: np.ndarray,
        face_boxes: list[FaceBox],
        average_confidence: float,
    ) -> dict:
        """Return a simple quality message for the frontend dashboard."""

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        average_brightness = float(np.mean(gray_frame))

        if average_brightness < 65:
            return {
                "status": "low_light",
                "message": "Low light can reduce detection accuracy.",
            }

        if not face_boxes:
            return {
                "status": "searching",
                "message": "No stable face is detected in this frame.",
            }

        if average_confidence < 85:
            return {
                "status": "medium",
                "message": "Detection is working, but face quality can improve.",
            }

        return {
            "status": "stable",
            "message": "Face detection is stable.",
        }


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
