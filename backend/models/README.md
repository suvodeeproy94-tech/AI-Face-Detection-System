# Face Detection Models

This folder stores model files used by the backend.

## Primary Model

```text
face_detector_model/face_detection_yunet_2023mar.onnx
```

This is the OpenCV YuNet face detector. It is lightweight, fast, and better
than Haar Cascade for real-time webcam face detection.

## Fallback Model

```text
haarcascade_frontalface_default.xml
```

This Haar Cascade model is kept as a fallback. The backend uses it only when
YuNet is not available.

## Accuracy Note

The project now uses stricter YuNet confidence filtering to reduce wrong
detections. A 95% accuracy claim still needs a labeled test dataset such as
WIDER FACE, FDDB, or a manually labeled webcam test set.
