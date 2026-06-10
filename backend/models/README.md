# Face Detection Models

This folder stores model files used by the backend.

## Current Model

```text
haarcascade_frontalface_default.xml
```

This is an OpenCV Haar Cascade model. It is lightweight and works well for a
beginner-friendly real-time webcam project.

## Accuracy Note

Haar Cascade is fast, but it may not always reach 95% accuracy in difficult
conditions such as low light, side faces, blur, or CCTV-style videos.

For a stronger future version, this project can be upgraded to:

- OpenCV DNN Face Detector
- SSD Face Detector
- RetinaFace
- YOLO face detection model
