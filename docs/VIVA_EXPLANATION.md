# Viva Explanation

## Project Title

AI-Based Real-Time Face Detection System

## Simple Definition

This project detects human faces from a live webcam feed. It draws a box around
each detected face, counts the faces, shows confidence, and stores detection
statistics in a local SQLite database.

## What This Project Does

- Opens webcam in the browser.
- Captures webcam frames using React.
- Sends frames to Flask backend.
- Uses OpenCV YuNet to detect faces.
- Returns face box positions and confidence.
- Draws boxes over the live video.
- Saves detection statistics in SQLite.

## What This Project Does Not Do

This project does not recognize people by name.

Example:

```text
Correct: Face detected
Not used: This person is Suvodeep
```

## Main Modules

| Module | Purpose |
|---|---|
| React frontend | Shows dashboard and webcam preview |
| Flask backend | Provides API routes |
| OpenCV YuNet | Detects faces |
| SQLite | Saves detection history |
| Tailwind CSS | Makes the UI clean and responsive |

## Main Workflow

```text
Webcam -> React -> Flask API -> OpenCV YuNet -> Face Boxes -> React Canvas
```

## Why YuNet Is Used

YuNet is used because it is lightweight and better than Haar Cascade for
real-time face detection. It is suitable for normal laptops and can run without
a heavy GPU.

## Why SQLite Is Used

SQLite is used because it is simple, local, and does not need a separate
database server. It is enough for saving detection history and statistics.

## Security And Privacy

- No password is stored.
- No API key is required.
- Face images are not saved by default.
- Webcam permission is controlled by the browser.
- The project detects faces only, it does not identify people.

## Accuracy Explanation

The system uses confidence filtering to reduce false detections. Final accuracy
must be tested with labeled images using the accuracy evaluation script.

The professional answer during viva is:

```text
The system targets 95% accuracy under controlled webcam conditions.
The final accuracy is measured using labeled test images and IoU-based matching.
```

## Limitations

- Low light can reduce accuracy.
- Very small or side-facing faces may be missed.
- Webcam quality affects the result.
- It detects faces, but does not recognize identities.

## Future Scope

- Add image upload detection.
- Add video upload detection.
- Add formal WIDER FACE evaluation.
- Add PDF report export.
- Add production deployment.
