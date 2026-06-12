# Accuracy Results

This document records the current measured accuracy results for the project.

The project is complete as a working real-time face detection system. It does
not claim 95% accuracy because the available evaluation reports do not prove
that target.

## Final Accuracy Statement

Use this statement in the report, README, and viva:

```text
This project uses OpenCV YuNet for real-time face detection.
It detects and counts faces from a webcam feed.
The best measured accuracy in the current evaluation is 91.15% on the
webcam-style WIDER FACE sample, so the project does not claim 95% accuracy.
```

## Current Evaluation Results

| Dataset Report | Images | Real Faces | Correct Detections | Missed Faces | Wrong Detections | Detection Accuracy | Precision | 95% Target |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| WIDER FACE sample | 100 | 324 | 168 | 156 | 0 | 51.85% | 100.00% | Not met |
| WIDER FACE closeup sample | 100 | 109 | 93 | 16 | 31 | 85.32% | 75.00% | Not met |
| WIDER FACE large sample | 100 | 167 | 148 | 19 | 72 | 88.62% | 67.27% | Not met |
| WIDER FACE webcam-style sample | 100 | 113 | 103 | 10 | 27 | 91.15% | 79.23% | Not met |

## Simple Meaning

Accuracy means how many real faces were correctly found.

Precision means how many predicted boxes were actually correct.

The webcam-style sample gives the best result because it is closer to the
main project use case, which is webcam-based face detection.

## Project Completion Decision

The project is complete for college submission, portfolio use, and viva
explanation because the main application works and the accuracy result is
documented honestly.

Reaching 95% accuracy is a future improvement, not a current project claim.
